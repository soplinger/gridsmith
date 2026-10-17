import random
import unittest

from gridsmith import core, solver
from gridsmith.solver import SearchLimitError

PUZZLE = "53..7....6..195....98....6.8...6...34..8.3..17...2...6.6....28....419..5....8..79"
SOLUTION = "534678912672195348198342567859761423426853791713924856961537284287419635345286179"


class SolverTests(unittest.TestCase):
    def test_solves_known_puzzle(self):
        solved = solver.solve(core.parse_puzzle(PUZZLE))
        self.assertEqual(core.to_line(solved), SOLUTION)

    def test_solution_satisfies_all_rules(self):
        solved = solver.solve(core.parse_puzzle(PUZZLE))
        self.assertEqual(core.conflicts(solved), [])
        self.assertTrue(all(solved))

    def test_unique_puzzle_has_one_solution(self):
        self.assertEqual(solver.count_solutions(core.parse_puzzle(PUZZLE)), 1)

    def test_blank_grid_stops_at_limit(self):
        self.assertEqual(solver.count_solutions(core.parse_puzzle("." * 81), limit=2), 2)

    def test_contradictory_clues_have_no_solution(self):
        values = core.parse_puzzle("55" + "." * 79)  # two 5s in row 1
        self.assertIsNone(solver.solve(values))
        self.assertEqual(solver.count_solutions(values), 0)

    def test_unsolvable_without_conflicts_has_no_solution(self):
        # Row 1 has 8 digits, the only one left for r1c9 is 9, but column 9 already holds 9.
        values = core.parse_puzzle("12345678." + "." * 72)
        values[8 + 9 * 8] = 9  # r9c9 = 9, so r1c9 cannot be 9 and has no candidate
        self.assertEqual(core.conflicts(values), [])
        self.assertEqual(solver.count_solutions(values), 0)

    def test_search_does_not_change_input(self):
        values = core.parse_puzzle(PUZZLE)
        before = list(values)
        solver.solve(values)
        self.assertEqual(values, before)

    def test_node_limit_is_enforced(self):
        with self.assertRaises(SearchLimitError):
            solver.search(core.parse_puzzle("." * 81), limit=2, node_limit=3)

    def test_wrong_size_grid_is_rejected(self):
        with self.assertRaises(ValueError):
            solver.search([0] * 80)

    def test_random_order_still_finds_valid_solution(self):
        rng = random.Random(3)
        full, _ = solver.search([0] * 81, limit=1, rng=rng)
        self.assertEqual(core.conflicts(full[0]), [])
        self.assertTrue(all(full[0]))


if __name__ == "__main__":
    unittest.main()
