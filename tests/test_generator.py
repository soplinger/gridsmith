import unittest

from gridsmith import core, generator, solver


class GeneratorTests(unittest.TestCase):
    def test_generated_puzzle_has_exactly_one_solution(self):
        puzzle = generator.generate(clues=30, seed=11)
        self.assertEqual(solver.count_solutions(puzzle), 1)

    def test_generated_puzzle_respects_clue_target(self):
        puzzle = generator.generate(clues=36, seed=5)
        givens = sum(1 for v in puzzle if v)
        self.assertGreaterEqual(givens, 36)
        self.assertLessEqual(givens, core.CELLS)

    def test_same_seed_gives_same_puzzle(self):
        self.assertEqual(generator.generate(clues=30, seed=99), generator.generate(clues=30, seed=99))

    def test_different_seeds_usually_differ(self):
        self.assertNotEqual(generator.generate(clues=30, seed=1), generator.generate(clues=30, seed=2))

    def test_clue_count_out_of_range_is_rejected(self):
        with self.assertRaises(ValueError):
            generator.generate(clues=16)
        with self.assertRaises(ValueError):
            generator.generate(clues=82)


if __name__ == "__main__":
    unittest.main()
