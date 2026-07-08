from __future__ import annotations

import random
from typing import Iterable

from cardapio.constants import DAYS, MANDATORY_SUNDAY_DINNER, SPECIAL_WEIGHTED_DISHES
from cardapio.storage import normalize_text


class MenuGenerationError(RuntimeError):
    """Erro ao montar o cardápio semanal."""


def _recipe_matches_keyword(recipe_name: str, keyword: str) -> bool:
    return keyword in normalize_text(recipe_name)


def _is_special_recipe(recipe_name: str) -> bool:
    normalized_name = normalize_text(recipe_name)
    return any(keyword in normalized_name for keyword in SPECIAL_WEIGHTED_DISHES)


def recipe_weight(recipe_name: str, day_name: str) -> int:
    if day_name not in ("Sexta-feira", "Sábado"):
        return 1
    return 2 if _is_special_recipe(recipe_name) else 1


def _find_cafe_recipe(recipes: Iterable[dict[str, object]]) -> dict[str, object] | None:
    normalized_target = MANDATORY_SUNDAY_DINNER
    for recipe in recipes:
        if normalize_text(recipe["name"]) == normalized_target:
            return recipe
    for recipe in recipes:
        if _recipe_matches_keyword(recipe["name"], normalized_target):
            return recipe
    return None


def _pick_recipe(
    candidates: list[dict[str, object]], day_name: str, rng: random.Random
) -> dict[str, object]:
    if not candidates:
        raise MenuGenerationError(f"Não há receitas suficientes para completar `{day_name}`.")
    weights = [recipe_weight(candidate["name"], day_name) for candidate in candidates]
    return rng.choices(candidates, weights=weights, k=1)[0]


def generate_weekly_menu(
    recipes: list[dict[str, object]], rng: random.Random | None = None
) -> list[dict[str, str]]:
    rng = rng or random.Random()
    cafe_recipe = _find_cafe_recipe(recipes)
    if cafe_recipe is None:
        raise MenuGenerationError("A receita `Café` é obrigatória para `Domingo / Janta`.")

    normalized_used = {normalize_text(cafe_recipe["name"])}
    unique_recipe_names = {normalize_text(recipe["name"]) for recipe in recipes}
    if len(unique_recipe_names) < 14:
        raise MenuGenerationError("Cadastre pelo menos 14 receitas únicas para montar a semana completa.")

    weekly_menu: list[dict[str, str]] = []

    for day_name in DAYS:
        available_for_lunch = [
            recipe for recipe in recipes if normalize_text(recipe["name"]) not in normalized_used
        ]
        lunch_recipe = _pick_recipe(available_for_lunch, day_name, rng)
        normalized_used.add(normalize_text(lunch_recipe["name"]))

        if day_name == "Domingo":
            dinner_recipe = cafe_recipe
        else:
            available_for_dinner = [
                recipe for recipe in recipes if normalize_text(recipe["name"]) not in normalized_used
            ]
            dinner_recipe = _pick_recipe(available_for_dinner, day_name, rng)
            normalized_used.add(normalize_text(dinner_recipe["name"]))

        weekly_menu.append(
            {
                "day": day_name,
                "lunch": str(lunch_recipe["name"]),
                "dinner": str(dinner_recipe["name"]),
            }
        )

    return weekly_menu


__all__ = ["DAYS", "MenuGenerationError", "generate_weekly_menu", "recipe_weight"]
