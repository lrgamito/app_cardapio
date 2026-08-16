from __future__ import annotations

import json
import random
from datetime import datetime
from pathlib import Path

import streamlit as st

from cardapio.auth import is_authenticated, logout, render_login_form
from cardapio.planner import MenuGenerationError, generate_weekly_menu
from cardapio.storage import (
    RECIPES_PATH,
    delete_recipe,
    ensure_data_files,
    load_recipes,
    normalize_text,
    save_recipe,
    sync_recipes,
)


def render_menu_table(weekly_menu: list[dict[str, str]]) -> None:
    rows: list[dict[str, str]] = []
    for item in weekly_menu:
        rows.append({"Dia": item["day"], "Refeição": "Almoço", "Prato": item["lunch"]})
        rows.append({"Dia": "", "Refeição": "Janta", "Prato": item["dinner"]})

    st.dataframe(rows, width="stretch", hide_index=True, height=531)


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
    if not is_authenticated():
        render_login_form()
        return

    st.subheader("Banco de receitas")

    st.caption(f"Banco local: `{RECIPES_PATH.name}`  ·  Usuário: `{st.session_state['authenticated_user']}`")

    if st.button("Sair", type="secondary"):
        logout()

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
        width="stretch",
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

    st.divider()
    st.subheader("Importar / Exportar banco de receitas")

    col_export, col_import = st.columns(2)

    with col_export:
        export_data = json.dumps(recipes, ensure_ascii=False, indent=2)
        timestamp = datetime.now().strftime("%Y-%m-%d")
        st.download_button(
            label="Exportar receitas (JSON)",
            data=export_data,
            file_name=f"receitas_{timestamp}.json",
            mime="application/json",
            use_container_width=True,
        )

    with col_import:
        uploaded = st.file_uploader(
            "Importar receitas (JSON)",
            type="json",
            label_visibility="collapsed",
        )
        if uploaded is not None:
            try:
                imported = json.loads(uploaded.read())
            except (json.JSONDecodeError, ValueError):
                st.error("Arquivo inválido. Envie um JSON com uma lista de receitas.")
                imported = None

            if imported is not None:
                if not isinstance(imported, list):
                    st.error("O JSON deve conter uma lista de receitas.")
                else:
                    try:
                        created, updated = sync_recipes(imported)
                        st.success(f"{created} receita(s) adicionadas, {updated} receita(s) atualizadas.")
                        st.rerun()
                    except ValueError as exc:
                        st.error(f"Erro na importação: {exc}")


def main() -> None:
    st.set_page_config(page_title="Cardápio Semanal", page_icon="🍽️", layout="wide")

    ensure_data_files()
    recipes = load_recipes()

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