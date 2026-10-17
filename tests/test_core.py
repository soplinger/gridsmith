import unittest

from gridsmith import core
from gridsmith.core import PuzzleError

PUZZLE = "53..7....6..195....98....6.8...6...34..8.3..17...2...6.6....28....419..5....8..79"
SOLUTION = (
    "534678912672195348198342567859761423426853791713924856961537284287419635345286179"
)


class ParseTests(unittest.TestCase):
    def test_zero_and_dot_both_mean_blank(self):
        with_dots = core.parse_puzzle("." * 81)
        with_zeros = core.parse_puzzle("0" * 81)
        self.assertEqual(with_dots, [0] * 81)
        self.assertEqual(with_zeros, [0] * 81)

    def test_spaces_and_tabs_are_ignored(self):
        spaced = "5 3 . . 7 . . . .\t" + PUZZLE[9:]
        self.assertEqual(core.parse_puzzle(spaced), core.parse_puzzle(PUZZLE))

    def test_wrong_length_reports_cell_count(self):
        with self.assertRaises(PuzzleError) as ctx:
            core.parse_puzzle(PUZZLE[:80], line=3)
        self.assertEqual(ctx.exception.line, 3)
        self.assertIn("expected 81 cells, found 80", str(ctx.exception))

    def test_bad_character_reports_column(self):
        bad = PUZZLE[:10] + "x" + PUZZLE[11:]
        with self.assertRaises(PuzzleError) as ctx:
            core.parse_puzzle(bad, line=2)
        self.assertEqual(ctx.exception.column, 11)
        self.assertEqual(ctx.exception.line, 2)
        self.assertIn("'x'", str(ctx.exception))

    def test_non_ascii_digit_is_rejected(self):
        bad = "٣" + PUZZLE[1:]
        with self.assertRaises(PuzzleError):
            core.parse_puzzle(bad)

    def test_digit_zero_is_not_a_clue(self):
        values = core.parse_puzzle(PUZZLE)
        self.assertEqual(values[2], 0)
        self.assertEqual(values[0], 5)

    def test_file_skips_comments_and_blank_lines_but_keeps_numbers(self):
        text = f"# header\n\n{PUZZLE}\n# note\n{SOLUTION}\n"
        parsed = core.parse_file(text)
        self.assertEqual([number for number, _ in parsed], [3, 5])

    def test_file_error_points_at_the_real_line(self):
        text = f"# header\n{PUZZLE}\n\n{PUZZLE}Z\n"
        with self.assertRaises(PuzzleError) as ctx:
            core.parse_file(text)
        self.assertEqual(ctx.exception.line, 4)

    def test_iter_handles_windows_line_endings(self):
        text = f"{PUZZLE}\r\n{SOLUTION}\r\n"
        numbers = [number for number, _ in core.iter_puzzle_lines(text)]
        self.assertEqual(numbers, [1, 2])


class FormatTests(unittest.TestCase):
    def test_line_round_trip(self):
        values = core.parse_puzzle(PUZZLE)
        self.assertEqual(core.to_line(values), PUZZLE)

    def test_grid_has_box_separators_and_nine_rows(self):
        text = core.format_grid(core.parse_puzzle(PUZZLE))
        lines = text.splitlines()
        self.assertEqual(len(lines), 11)
        self.assertEqual(lines.count("------+-------+------"), 2)
        self.assertEqual(lines[0], "5 3 . | . 7 . | . . .")


class RuleTests(unittest.TestCase):
    def test_valid_solution_has_no_conflicts(self):
        self.assertEqual(core.conflicts(core.parse_puzzle(SOLUTION)), [])

    def test_duplicate_in_row_is_reported_with_cells(self):
        values = core.parse_puzzle(PUZZLE)
        values[1] = 5  # r1c2 is 5 too, and r1c1 is already 5
        problems = core.conflicts(values)
        self.assertIn("row 1 has digit 5 at r1c1, r1c2", problems)

    def test_duplicate_in_box_is_reported(self):
        values = [0] * 81
        values[0] = 9  # r1c1
        values[20] = 9  # r3c3, same box, different row and column
        problems = core.conflicts(values)
        self.assertEqual(problems, ["box 1 has digit 9 at r1c1, r3c3"])

    def test_candidates_exclude_peer_digits(self):
        values = core.parse_puzzle(PUZZLE)
        cand = core.candidates(values)
        # r1c3: row 1 holds 5, 3, 7; column 3 holds 8; box 1 holds 5, 3, 6, 9, 8
        self.assertEqual(cand[2], {1, 2, 4})
        self.assertEqual(cand[0], set())  # r1c1 is a clue

    def test_labels_are_one_based(self):
        self.assertEqual(core.label(0), "r1c1")
        self.assertEqual(core.label(80), "r9c9")


if __name__ == "__main__":
    unittest.main()
