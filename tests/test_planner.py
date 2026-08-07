from __future__ import annotations

import random
import unittest

from cardapio.constants import DAYS
from cardapio.planner import generate_weekly_menu, recipe_weight


class PlannerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.recipes = [
            {"name": "Café", "ingredients": ["Pão", "Café"]},
            {"name": "Hamburguer", "ingredients": ["Pão", "Carne"]},
            {"name": "Pizza", "ingredients": ["Massa", "Queijo"]},
            {"name": "Esfiha", "ingredients": ["Massa", "Carne"]},
            {"name": "Lanche Natural", "ingredients": ["Pão", "Frango"]},
        ] + [
            {"name": f"Prato {index}", "ingredients": [f"Ingrediente {index}"]}
            for index in range(1, 20)
        ]

    def test_generates_seven_days_without_repetition(self) -> None:
        weekly_menu = generate_weekly_menu(self.recipes, rng=random.Random(7))
        self.assertEqual(DAYS, [item["day"] for item in weekly_menu])
        self.assertEqual("Café", weekly_menu[0]["dinner"])

        chosen_dishes = [item["lunch"] for item in weekly_menu] + [item["dinner"] for item in weekly_menu]
        self.assertEqual(len(chosen_dishes), len(set(chosen_dishes)))

    def test_special_weight_is_higher_on_friday_and_saturday(self) -> None:
        self.assertEqual(2, recipe_weight("Hamburguer", "Sexta-feira"))
        self.assertEqual(2, recipe_weight("Lanche Natural", "Sábado"))
        self.assertEqual(1, recipe_weight("Pizza", "Quarta-feira"))
        self.assertEqual(1, recipe_weight("Carne de Panela", "Sábado"))

    def test_weighted_dishes_appear_more_on_weighted_days(self) -> None:
        weekend_special_hits = 0
        midweek_special_hits = 0
        runs = 300
        specials = {"hamburguer", "pizza", "esfiha", "lanche natural"}

        for seed in range(runs):
            weekly_menu = generate_weekly_menu(self.recipes, rng=random.Random(seed))
            weekend_slots = weekly_menu[5:7]
            midweek_slots = weekly_menu[1:5]

            for item in weekend_slots:
                weekend_special_hits += int(item["lunch"].lower() in specials)
                weekend_special_hits += int(item["dinner"].lower() in specials)
            for item in midweek_slots:
                midweek_special_hits += int(item["lunch"].lower() in specials)
                midweek_special_hits += int(item["dinner"].lower() in specials)

        weekend_rate = weekend_special_hits / (runs * 4)
        midweek_rate = midweek_special_hits / (runs * 8)
        self.assertGreater(weekend_rate, midweek_rate)


if __name__ == "__main__":
    unittest.main()