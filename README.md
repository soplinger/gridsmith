# Gridsmith

**An offline Sudoku toolkit: parse, check, solve, rate, hint and generate puzzles from the command line.**

Gridsmith reads plain-text puzzles, tells you exactly where a puzzle is broken, solves it with a
bounded search, proves whether the answer is unique, rates how hard it is by the techniques it needs,
gives a human-style hint, checks your partial work, and generates new puzzles from a seed.
It uses only the Python 3 standard library. There is no network access, no account, and no data file
beyond the puzzle text you pass in.

## Features

- **Strict parsing**: accepts `0` or `.` for blanks, ignores spaces and tabs, and rejects anything else
  with the line and column of the bad character.
- **Batch validation**: `batch` checks every puzzle in a file, one per line, and reports each problem
  with its line number. Comments (`#`) and blank lines are skipped.
- **Boxed grid display**: `show` prints a puzzle with box separators and its clue count.
- **Rule conflict finder**: `check` names every row, column or box where a digit repeats, with the cells involved.
- **Solver with a node cap**: `solve` uses backtracking that always fills the most constrained blank first,
  and stops with a clear error instead of hanging on a bad puzzle.
- **Uniqueness and solution counting**: `count` and `check` report whether a puzzle has one solution,
  none, or several.
- **Pencil marks**: `marks` prints the candidate digits still possible in every blank.
- **Difficulty rating**: `rate` labels a puzzle `easy`, `medium`, `hard` or `expert` depending on whether
  naked singles, hidden singles, or search are needed.
- **Hints that explain themselves**: `hint` names the next deduction, such as
  "r5c5 has only one candidate left: 7" or "7 can only go in r5c5 within row 5".
- **Attempt checking**: `verify` compares a partly filled grid with the solution, lists wrong cells,
  and refuses an attempt that changes a given clue.
- **Seeded generation**: `generate` builds a puzzle with a unique solution and a target number of clues.
  The same seed always gives the same puzzle.
- **Single-line or grid output**: `solve` and `generate` take `--oneline` to print 81 characters
  instead of the boxed grid, which is easy to paste into other tools.

## Quick start

Gridsmith runs from this directory with `python3 -m gridsmith`.

```bash
python3 -m gridsmith show 53..7....6..195....98....6.8...6...34..8.3..17...2...6.6....28....419..5....8..79
```

Output:

```
5 3 . | . 7 . | . . .
6 . . | 1 9 5 | . . .
. 9 8 | . . . | . 6 .
------+-------+------
8 . . | . 6 . | . . 3
4 . . | 8 . 3 | . . 1
7 . . | . 2 . | . . 6
------+-------+------
. 6 . | . . . | 2 8 .
. . . | 4 1 9 | . . 5
. . . | . 8 . | . 7 9
clues: 30
```

Check a file of puzzles, including a deliberately broken one:

```bash
python3 -m gridsmith batch examples/broken.txt
```

Each problem is reported on its own line, with the line number where it occurs:

```
line 2: expected 81 cells, found 80
line 3, column 82: unexpected character 'x'
line 4: conflict: row 1 has digit 5 at r1c1, r1c2
3 puzzles: 0 ok, 3 with problems
```

Exit status is `0` only when every puzzle is valid, so `batch` works in scripts.

## How to run

Gridsmith needs Python 3.8 or newer and nothing else.

| Command | What it does |
| --- | --- |
| `show PUZZLE` | Print the boxed grid and the clue count |
| `check PUZZLE` | List rule conflicts and say whether the solution is unique |
| `solve PUZZLE [--oneline]` | Print the solution |
| `count PUZZLE [--limit N]` | Count solutions up to a limit |
| `marks PUZZLE` | Show pencil marks for every blank |
| `rate PUZZLE` | Rate difficulty and show how many singles and search nodes were needed |
| `hint PUZZLE` | Describe the next deduction |
| `verify PUZZLE --attempt 81CHARS` | Check your partial answer |
| `generate [--clues N] [--seed S] [--oneline]` | Generate a unique-solution puzzle |
| `batch FILE` | Validate every puzzle in a file, one per line |

For commands that take a single puzzle, you can pass the 81 characters directly, or read one
puzzle from a file with `--file FILE` (add `--line N` if the file holds several).

```bash
python3 -m gridsmith solve --file examples/puzzles.txt --line 5 --oneline
python3 -m gridsmith generate --clues 28 --seed 42
```

Puzzle format: 81 cells, row by row. Digits are clues, `0` and `.` are blanks, and whitespace is ignored.
Files hold one puzzle per line. Lines that start with `#` and blank lines are skipped.

## How to test

```bash
python3 -m pytest
```

or, without pytest:

```bash
python3 -m unittest discover tests
```

The tests cover parsing errors and line numbers, the rule checks, the solver and its node cap,
uniqueness counting, generation (uniqueness and reproducibility), rating, hints, attempt
checking, and the CLI exit codes and output.

## Project layout

```
gridsmith/
  core.py       parsing, formatting, rule checks, candidates
  solver.py     backtracking search with a node cap
  generator.py  seeded puzzle generation with uniqueness checks
  analysis.py   difficulty rating, hints, attempt checking
  cli.py        argparse commands
examples/
  puzzles.txt   valid sample puzzles
  broken.txt    deliberately invalid input for batch
tests/          unit tests for each module and the CLI
```

## Limits

- Only the classic 9x9 Sudoku with 3x3 boxes is supported.
- Difficulty rating uses the singles techniques and a search; it does not recognise advanced patterns
  such as X-wings, so `hard` and `expert` mean "needed search", not a fixed human scale.
- Generated puzzles are built greedily. The clue count can end above the target when no further clue
  can be removed without losing uniqueness, and the CLI says so.
