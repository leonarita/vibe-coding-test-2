import unittest

from app.draw import draw_winners, unique_participants


class DrawTests(unittest.TestCase):
    def test_unique_participants_preserves_first_order(self):
        authors = ["Ana", "João", "Ana", "Maria", "João"]
        self.assertEqual(unique_participants(authors), ["Ana", "João", "Maria"])

    def test_draw_winners_with_seed_is_reproducible(self):
        participants = ["Ana", "João", "Maria", "Pedro"]
        winners1 = draw_winners(participants, 2, seed=7)
        winners2 = draw_winners(participants, 2, seed=7)
        self.assertEqual(winners1, winners2)

    def test_draw_winners_validates_count(self):
        participants = ["Ana", "João"]
        with self.assertRaises(ValueError):
            draw_winners(participants, 3)


if __name__ == "__main__":
    unittest.main()
