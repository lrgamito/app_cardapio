from __future__ import annotations

import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from cardapio.storage import normalize_text


MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
NS = {"a": MAIN_NS}


class SpreadsheetImportError(RuntimeError):
    """Erro de importação da planilha de receitas."""


def _column_from_ref(cell_ref: str) -> str:
    letters = []
    for char in cell_ref:
        if char.isalpha():
            letters.append(char)
        else:
            break
    return "".join(letters)


def _load_shared_strings(archive: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []
    root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    strings: list[str] = []
    for item in root:
        chunks = [node.text or "" for node in item.iter(f"{{{MAIN_NS}}}t")]
        strings.append("".join(chunks))
    return strings


def _read_cell(cell: ET.Element, shared_strings: list[str]) -> str:
    value_node = cell.find("a:v", NS)
    if value_node is None or value_node.text is None:
        return ""
    value = value_node.text
    if cell.attrib.get("t") == "s":
        return shared_strings[int(value)]
    return value


def _resolve_sheet_path(archive: zipfile.ZipFile, sheet_name: str) -> str:
    workbook = ET.fromstring(archive.read("xl/workbook.xml"))
    rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    rel_map = {rel.attrib["Id"]: rel.attrib["Target"] for rel in rels.findall(f"{{{PKG_REL_NS}}}Relationship")}

    sheets = workbook.find("a:sheets", NS)
    if sheets is None:
        raise SpreadsheetImportError("A planilha não possui abas legíveis.")

    for sheet in sheets:
        if sheet.attrib.get("name") == sheet_name:
            rel_id = sheet.attrib[f"{{{REL_NS}}}id"]
            target = rel_map[rel_id].lstrip("/")
            return target if target.startswith("xl/") else f"xl/{target}"

    raise SpreadsheetImportError(f"A aba obrigatória `{sheet_name}` não foi encontrada.")


def load_recipes_from_workbook(path: str | Path, sheet_name: str = "Página1") -> list[dict[str, object]]:
    workbook_path = Path(path)
    if not workbook_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {workbook_path}")

    with zipfile.ZipFile(workbook_path) as archive:
        sheet_path = _resolve_sheet_path(archive, sheet_name)
        shared_strings = _load_shared_strings(archive)
        worksheet = ET.fromstring(archive.read(sheet_path))

    rows = worksheet.findall("a:sheetData/a:row", NS)
    if not rows:
        raise SpreadsheetImportError("A aba está vazia.")

    header_map: dict[str, str] = {}
    for cell in rows[0].findall("a:c", NS):
        header_map[_column_from_ref(cell.attrib.get("r", ""))] = _read_cell(cell, shared_strings)

    dish_column = next(
        (column for column, header in header_map.items() if normalize_text(header) == "prato"),
        None,
    )
    ingredient_columns = [
        column
        for column, header in header_map.items()
        if normalize_text(header).startswith("ingrediente")
    ]

    if dish_column is None:
        raise SpreadsheetImportError("A coluna obrigatória `Prato` não foi encontrada.")

    recipes: list[dict[str, object]] = []
    seen_names: set[str] = set()

    for row in rows[1:]:
        cell_map = {
            _column_from_ref(cell.attrib.get("r", "")): _read_cell(cell, shared_strings)
            for cell in row.findall("a:c", NS)
        }
        dish_name = str(cell_map.get(dish_column, "")).strip()
        if not dish_name:
            continue

        normalized_name = normalize_text(dish_name)
        if normalized_name in seen_names:
            continue

        ingredients = [str(cell_map.get(column, "")).strip() for column in ingredient_columns if str(cell_map.get(column, "")).strip()]
        if not ingredients:
            continue

        recipes.append({"name": dish_name, "ingredients": ingredients, "source": "xlsx"})
        seen_names.add(normalized_name)

    if not recipes:
        raise SpreadsheetImportError("Nenhuma receita válida foi encontrada na planilha.")

    return recipes
