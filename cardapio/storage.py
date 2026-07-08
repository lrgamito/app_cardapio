from __future__ import annotations

import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any

import json


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RECIPES_PATH = DATA_DIR / "recipes.json"


def ensure_data_files() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not RECIPES_PATH.exists():
        RECIPES_PATH.write_text("[]\n", encoding="utf-8")


def normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFD", value.strip())
    without_accents = "".join(char for char in normalized if unicodedata.category(char) != "Mn")
    return " ".join(without_accents.lower().split())


def _read_json(path: Path, fallback: Any) -> Any:
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_recipes() -> list[dict[str, Any]]:
    ensure_data_files()
    recipes = _read_json(RECIPES_PATH, [])
    return sorted(recipes, key=lambda recipe: normalize_text(recipe["name"]))


def save_recipes(recipes: list[dict[str, Any]]) -> None:
    ensure_data_files()
    _write_json(RECIPES_PATH, recipes)


def _validate_recipe(recipe: dict[str, Any]) -> dict[str, Any]:
    name = str(recipe.get("name", "")).strip()
    if not name:
        raise ValueError("Informe o nome da receita.")

    ingredients = [
        str(ingredient).strip()
        for ingredient in recipe.get("ingredients", [])
        if str(ingredient).strip()
    ]
    if not ingredients:
        raise ValueError("Informe pelo menos um ingrediente.")

    return {
        "name": name,
        "ingredients": ingredients,
        "source": recipe.get("source", "manual"),
        "updated_at": datetime.now().isoformat(timespec="seconds"),
    }


def save_recipe(recipe: dict[str, Any]) -> dict[str, Any]:
    validated = _validate_recipe(recipe)
    recipes = load_recipes()
    normalized_name = normalize_text(validated["name"])

    updated = False
    for index, current in enumerate(recipes):
        if normalize_text(current["name"]) == normalized_name:
            recipes[index] = validated
            updated = True
            break

    if not updated:
        recipes.append(validated)

    save_recipes(sorted(recipes, key=lambda item: normalize_text(item["name"])))
    return validated


def delete_recipe(name: str) -> None:
    normalized_name = normalize_text(name)
    recipes = [recipe for recipe in load_recipes() if normalize_text(recipe["name"]) != normalized_name]
    save_recipes(recipes)


def sync_recipes(imported_recipes: list[dict[str, Any]]) -> tuple[int, int]:
    recipes = load_recipes()
    index_by_name = {normalize_text(recipe["name"]): idx for idx, recipe in enumerate(recipes)}
    created = 0
    updated = 0

    for recipe in imported_recipes:
        validated = _validate_recipe(recipe)
        normalized_name = normalize_text(validated["name"])
        if normalized_name in index_by_name:
            recipes[index_by_name[normalized_name]] = validated
            updated += 1
        else:
            recipes.append(validated)
            index_by_name[normalized_name] = len(recipes) - 1
            created += 1

    save_recipes(sorted(recipes, key=lambda item: normalize_text(item["name"])))
    return created, updated
