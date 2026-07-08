from __future__ import annotations

import random
from pathlib import Path

import streamlit as st

from cardapio.planner import MenuGenerationError, generate_weekly_menu
from cardapio.spreadsheet import SpreadsheetImportError, load_recipes_from_workbook
from cardapio.storage import (
    RECIPES_PATH,
    delete_recipe,
    ensure_data_files,
    load_recipes,
    normalize_text,
    save_recipe,
    sync_recipes,
)


BASE_DIR = Path(__file__).resolve().parent
WORKBOOK_PATH = BASE_DIR / "Receitas Dia a Dia.xlsx"


def render_menu_table(weekly_menu: list[dict[str, str]]) -> None:
    rows: list[dict[str, str]] = []
    for item in weekly_menu:
        rows.append({"Dia": item["day"], "Refeição": "Almoço", "Prato": item["lunch"]})
        rows.append({"Dia": "", "Refeição": "Janta", "Prato": item["dinner"]})

    st.dataframe(rows, use_container_width=True, hide_index=True, height=531)


def bootstrap_recipes() -> tuple[int, int]:
    if not WORKBOOK_PATH.exists():
        return 0, 0
    imported = load_recipes_from_workbook(WORKBOOK_PATH)
    return sync_recipes(imported)


def render_menu_tab(recipes: list[dict[str, object]]) -> None:
    st.subheader("Planejamento semanal")
    st.info(
        "7 dias fixos, sem repetir prato na mesma semana. Sexta e sábado recebem peso maior para "
        "`Hamburguer`, `Pizza`, `Esfiha` e `Lanche`. Domingo na janta é sempre `Café`."
    )

    has_cafe = any("cafe" == normalize_text(recipe["name"]) for recipe in recipes)
    if not has_cafe:
        st.warning("Cadastre a receita `Café` na aba `Receitas` para liberar a geração do cardápio.")

    if st.button("Gerar cardápio semanal", type="primary", disabled=not has_cafe):
        try:
            st.session_state["weekly_menu"] = generate_weekly_menu(recipes, rng=random.Random())
        except MenuGenerationError as exc:
            st.error(str(exc))

    weekly_menu = st.session_state.get("weekly_menu")
    if weekly_menu:
        render_menu_table(weekly_menu)


def render_recipes_tab(recipes: list[dict[str, object]]) -> None:
    st.subheader("Banco de receitas")

    left, right = st.columns([1, 1])
    with left:
        st.caption(f"Fonte principal: `{WORKBOOK_PATH.name}`")
    with right:
        if st.button("Importar / sincronizar planilha", use_container_width=True):
            try:
                imported = load_recipes_from_workbook(WORKBOOK_PATH)
                created, updated = sync_recipes(imported)
                st.success(f"Sincronização concluída: {created} criadas, {updated} atualizadas.")
                st.rerun()
            except (FileNotFoundError, SpreadsheetImportError) as exc:
                st.error(str(exc))

    search = normalize_text(st.text_input("Buscar receitas", placeholder="Ex.: frango, lanche, sopa"))
    filtered = [
        recipe
        for recipe in recipes
        if not search
        or search in normalize_text(recipe["name"])
        or any(search in normalize_text(ingredient) for ingredient in recipe["ingredients"])
    ]

    st.dataframe(
        [
            {
                "Receita": recipe["name"],
                "Ingredientes": len(recipe["ingredients"]),
                "Origem": recipe.get("source", "manual"),
            }
            for recipe in filtered
        ],
        use_container_width=True,
        hide_index=True,
    )

    options = ["Nova receita"] + [recipe["name"] for recipe in recipes]
    selected_name = st.selectbox("Editar receita", options=options)
    selected_recipe = next((recipe for recipe in recipes if recipe["name"] == selected_name), None)

    with st.form("recipe_form", clear_on_submit=False):
        recipe_name = st.text_input(
            "Nome da receita",
            value=selected_recipe["name"] if selected_recipe else "",
            placeholder="Ex.: Pizza, Café, Esfiha de carne",
        )
        ingredient_lines = "\n".join(selected_recipe["ingredients"]) if selected_recipe else ""
        ingredients_text = st.text_area(
            "Ingredientes (um por linha)",
            value=ingredient_lines,
            height=180,
            placeholder="Ingrediente 1\nIngrediente 2\nIngrediente 3",
        )
        save_clicked = st.form_submit_button("Salvar receita", type="primary")

        if save_clicked:
            ingredients = [line.strip() for line in ingredients_text.splitlines() if line.strip()]
            try:
                save_recipe(
                    {
                        "name": recipe_name,
                        "ingredients": ingredients,
                        "source": selected_recipe.get("source", "manual") if selected_recipe else "manual",
                    }
                )
            except ValueError as exc:
                st.error(str(exc))
            else:
                st.success("Receita salva com sucesso.")
                st.rerun()

    if selected_recipe and st.button("Excluir receita selecionada"):
        delete_recipe(selected_recipe["name"])
        st.success("Receita removida.")
        st.rerun()


def main() -> None:
    st.set_page_config(page_title="Cardápio Semanal", page_icon="🍽️", layout="wide")

    ensure_data_files()
    recipes = load_recipes()
    if not recipes and WORKBOOK_PATH.exists():
        try:
            created, updated = bootstrap_recipes()
            recipes = load_recipes()
            if created or updated:
                st.toast(
                    f"Base inicial importada da planilha: {created} criadas, {updated} atualizadas.",
                    icon="📥",
                )
        except SpreadsheetImportError as exc:
            st.warning(f"Não foi possível importar a planilha automaticamente: {exc}")

    st.title("🍽️ App de Cardápio Semanal")
    st.caption("Gerencie receitas e gere uma semana inteira de pratos.")

    tab_menu, tab_recipes = st.tabs(["Cardápio semanal", "Receitas"])

    with tab_menu:
        render_menu_tab(recipes)
    with tab_recipes:
        render_recipes_tab(recipes)

    st.caption(f"Banco textual local: `{RECIPES_PATH.name}`")


if __name__ == "__main__":
    main()
