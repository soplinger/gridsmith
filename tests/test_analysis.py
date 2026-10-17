import unittest

from gridsmith import analysis, core

PUZZLE = "53..7....6..195....98....6.8...6...34..8.3..17...2...6.6....28....419..5....8..79"
SOLUTION = "534678912672195348198342567859761423426853791713924856961537284287419635345286179"


class RateTests(unittest.TestCase):
    def test_one_blank_is_easy_naked_single(self):
        values = core.parse_puzzle(SOLUTION)
        values[40] = 0
        rating, detail = analysis.rate(values)
        self.assertEqual(rating, analysis.EASY)
        self.assertEqual(detail["naked"], 1)
        self.assertEqual(detail["hidden"], 0)

    def test_classic_puzzle_gets_a_known_rating(self):
        rating, detail = analysis.rate(core.parse_puzzle(PUZZLE))
        self.assertIn(rating, {analysis.EASY, analysis.MEDIUM, analysis.HARD, analysis.EXPERT})
        self.assertGreaterEqual(detail["naked"], 0)
        self.assertGreaterEqual(detail["hidden"], 0)
        self.assertGreaterEqual(detail["search_nodes"], 0)

    def test_blank_grid_is_not_rated(self):
        with self.assertRaises(ValueError) as ctx:
            analysis.rate(core.parse_puzzle("." * 81))
        self.assertIn("more than one solution", str(ctx.exception))

    def test_conflicting_clues_are_not_rated(self):
        with self.assertRaises(ValueError) as ctx:
            analysis.rate(core.parse_puzzle("55" + "." * 79))
        self.assertIn("conflicting clues", str(ctx.exception))


class HintTests(unittest.TestCase):
    def test_hint_gives_the_solution_digit_for_a_single(self):
        values = core.parse_puzzle(SOLUTION)
        values[40] = 0
        idx, digit, text = analysis.hint(values)
        self.assertEqual(idx, 40)
        self.assertEqual(digit, int(SOLUTION[40]))
        self.assertIn("r5c5", text)

    def test_hint_on_complete_grid_is_an_error(self):
        with self.assertRaises(ValueError):
            analysis.hint(core.parse_puzzle(SOLUTION))

    def test_hint_on_puzzle_without_solution_is_an_error(self):
        with self.assertRaises(ValueError):
            analysis.hint(core.parse_puzzle("55" + "." * 79))

    def test_hint_for_puzzle_is_a_real_deduction(self):
        values = core.parse_puzzle(PUZZLE)
        idx, digit, text = analysis.hint(values)
        self.assertEqual(int(SOLUTION[idx]), digit)
        self.assertTrue(text)


class AttemptTests(unittest.TestCase):
    def test_reports_wrong_cell_and_blank_count(self):
        puzzle = core.parse_puzzle(PUZZLE)
        attempt = core.parse_puzzle(SOLUTION)
        attempt[2] = 1  # r1c3 should be 4
        attempt[3] = 0  # r1c4 left blank
        wrong, blanks = analysis.check_attempt(puzzle, attempt)
        self.assertEqual(wrong, [2])
        self.assertEqual(blanks, 1)

    def test_fully_correct_attempt_has_no_wrong_cells(self):
        puzzle = core.parse_puzzle(PUZZLE)
        wrong, blanks = analysis.check_attempt(puzzle, core.parse_puzzle(SOLUTION))
        self.assertEqual(wrong, [])
        self.assertEqual(blanks, 0)

    def test_changing_a_given_clue_is_rejected(self):
        puzzle = core.parse_puzzle(PUZZLE)
        attempt = core.parse_puzzle(SOLUTION)
        attempt[0] = 1  # r1c1 is a clue of 5
        with self.assertRaises(ValueError) as ctx:
            analysis.check_attempt(puzzle, attempt)
        self.assertIn("r1c1", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
