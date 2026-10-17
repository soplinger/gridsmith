import contextlib
import io
import os
import unittest

from gridsmith import cli, core

HERE = os.path.dirname(os.path.abspath(__file__))
EXAMPLES = os.path.join(HERE, "..", "examples")
PUZZLE = "53..7....6..195....98....6.8...6...34..8.3..17...2...6.6....28....419..5....8..79"
SOLUTION = "534678912672195348198342567859761423426853791713924856961537284287419635345286179"


def run(argv):
    """Run the CLI, returning (exit code, stdout text)."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = cli.main(argv)
    return code, out.getvalue()


class CliTests(unittest.TestCase):
    def test_show_prints_grid_and_clue_count(self):
        code, text = run(["show", PUZZLE])
        self.assertEqual(code, 0)
        self.assertIn("5 3 . | . 7 . | . . .", text)
        self.assertIn("clues:", text)

    def test_solve_oneline_prints_solution(self):
        code, text = run(["solve", PUZZLE, "--oneline"])
        self.assertEqual(code, 0)
        self.assertEqual(text.strip(), SOLUTION)

    def test_check_flags_conflict_with_exit_one(self):
        code, text = run(["check", "55" + "." * 79])
        self.assertEqual(code, 1)
        self.assertIn("conflict: row 1 has digit 5", text)

    def test_check_passes_unique_puzzle(self):
        code, text = run(["check", PUZZLE])
        self.assertEqual(code, 0)
        self.assertIn("unique solution", text)

    def test_verify_reports_wrong_cells(self):
        attempt = list(SOLUTION)
        attempt[2] = "1"
        code, text = run(["verify", PUZZLE, "--attempt", "".join(attempt)])
        self.assertEqual(code, 1)
        self.assertIn("1 wrong: r1c3", text)

    def test_verify_accepts_correct_attempt(self):
        code, text = run(["verify", PUZZLE, "--attempt", SOLUTION])
        self.assertEqual(code, 0)
        self.assertIn("all filled cells are correct", text)

    def test_bad_puzzle_gives_error_exit_two(self):
        out = io.StringIO()
        with contextlib.redirect_stderr(out), contextlib.redirect_stdout(io.StringIO()):
            code = cli.main(["show", "123"])
        self.assertEqual(code, 2)
        self.assertIn("expected 81 cells, found 3", out.getvalue())

    def test_batch_reports_each_problem_with_its_line_number(self):
        code, text = run(["batch", os.path.join(EXAMPLES, "broken.txt")])
        self.assertEqual(code, 1)
        self.assertIn("line 2: expected 81 cells, found 80", text)
        self.assertIn("line 3, column 82: unexpected character 'x'", text)
        self.assertIn("line 4: conflict: row 1 has digit 5", text)

    def test_batch_passes_the_sample_file(self):
        code, text = run(["batch", os.path.join(EXAMPLES, "puzzles.txt")])
        self.assertEqual(code, 0)
        self.assertIn("2 puzzles: 2 ok, 0 with problems", text)

    def test_generate_is_reproducible_from_seed(self):
        first = run(["generate", "--seed", "4", "--clues", "30", "--oneline"])[1]
        second = run(["generate", "--seed", "4", "--clues", "30", "--oneline"])[1]
        self.assertEqual(first, second)
        self.assertEqual(len(first.strip()), core.CELLS)

    def test_marks_prints_candidates(self):
        code, text = run(["marks", PUZZLE])
        self.assertEqual(code, 0)
        self.assertIn("124", text)


if __name__ == "__main__":
    unittest.main()
