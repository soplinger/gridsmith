"""Command-line interface. Run as ``python3 -m gridsmith <command> ...``."""

import argparse
import sys

from . import analysis, core, generator, solver
from .core import PuzzleError

ERRORS = (PuzzleError, ValueError, OSError, solver.SearchLimitError)


def _add_source(parser):
    parser.add_argument("puzzle", nargs="?", help="81 cells; digits, 0 or . for blanks")
    parser.add_argument("--file", help="read the puzzle from a file, one per line")
    parser.add_argument("--line", type=int, help="which line of --file to use")


def _load_puzzle(args):
    if args.file and args.puzzle is not None:
        raise PuzzleError("give either a puzzle string or --file, not both")
    if args.line is not None and not args.file:
        raise PuzzleError("--line only applies with --file")
    if args.file:
        with open(args.file, encoding="utf-8-sig") as handle:
            puzzles = core.parse_file(handle.read())
        if not puzzles:
            raise PuzzleError(f"{args.file} contains no puzzles")
        if args.line is None:
            if len(puzzles) > 1:
                raise PuzzleError(f"{args.file} has {len(puzzles)} puzzles; choose one with --line")
            return puzzles[0][1]
        for number, values in puzzles:
            if number == args.line:
                return values
        raise PuzzleError(f"no puzzle on line {args.line} of {args.file}", args.line)
    if args.puzzle is None:
        raise PuzzleError("give a puzzle string or --file")
    return core.parse_puzzle(args.puzzle)


def _solution_text(count):
    return "no solution" if count == 0 else ("unique solution" if count == 1 else "multiple solutions")


def cmd_show(args):
    values = _load_puzzle(args)
    print(core.format_grid(values))
    print(f"clues: {sum(1 for v in values if v)}")
    return 0


def cmd_check(args):
    values = _load_puzzle(args)
    problems = core.conflicts(values)
    for problem in problems:
        print(f"conflict: {problem}")
    if problems:
        return 1
    count = solver.count_solutions(values)
    label = "2 or more solutions" if count == 2 else _solution_text(count)
    print(f"no conflicts; {label}")
    return 0 if count == 1 else 1


def cmd_solve(args):
    values = _load_puzzle(args)
    solution = solver.solve(values, node_limit=args.node_limit)
    if solution is None:
        print("no solution")
        return 1
    print(core.to_line(solution) if args.oneline else core.format_grid(solution))
    return 0


def cmd_count(args):
    if args.limit < 1:
        raise ValueError("--limit must be at least 1")
    values = _load_puzzle(args)
    count = solver.count_solutions(values, limit=args.limit, node_limit=args.node_limit)
    shown = f"{count} or more" if count == args.limit else str(count)
    print(f"solutions: {shown}")
    return 0


def cmd_marks(args):
    values = _load_puzzle(args)
    marks = core.candidates(values)
    width = 10
    band = "-" * (width * core.BOX)
    separator = "+".join([band] * core.BOX)
    for r in range(core.SIZE):
        if r and r % core.BOX == 0:
            print(separator)
        cells = []
        for c in range(core.SIZE):
            idx = r * core.SIZE + c
            text = "".join(str(d) for d in sorted(marks[idx])) if not values[idx] else str(values[idx])
            cells.append(text.ljust(width))
        groups = ["".join(cells[i:i + core.BOX]) for i in range(0, core.SIZE, core.BOX)]
        print("|".join(groups).rstrip())
    return 0


def cmd_rate(args):
    values = _load_puzzle(args)
    rating, detail = analysis.rate(values)
    print(f"rating: {rating}")
    print(f"naked singles: {detail['naked']}, hidden singles: {detail['hidden']}, "
          f"search nodes: {detail['search_nodes']}")
    return 0


def cmd_hint(args):
    values = _load_puzzle(args)
    _, _, text = analysis.hint(values)
    print(text)
    return 0


def cmd_verify(args):
    puzzle = _load_puzzle(args)
    attempt = core.parse_puzzle(args.attempt)
    wrong, blanks = analysis.check_attempt(puzzle, attempt)
    if wrong:
        names = ", ".join(core.label(i) for i in wrong)
        print(f"{len(wrong)} wrong: {names}")
        return 1
    print(f"all filled cells are correct; {blanks} blank" + ("" if blanks == 1 else "s") + " left")
    return 0


def cmd_generate(args):
    puzzle = generator.generate(clues=args.clues, seed=args.seed)
    if args.oneline:
        print(core.to_line(puzzle))
        return 0
    print(core.format_grid(puzzle))
    givens = sum(1 for v in puzzle if v)
    print(f"clues: {givens}")
    if givens > args.clues:
        print(f"note: could not reach {args.clues} clues while keeping one solution")
    return 0


def _batch_line(number, raw, node_limit):
    try:
        values = core.parse_puzzle(raw, number)
    except PuzzleError as exc:
        return False, f"{exc}"
    problems = core.conflicts(values)
    if problems:
        return False, f"line {number}: conflict: {problems[0]}"
    try:
        count = solver.count_solutions(values, node_limit=node_limit)
    except solver.SearchLimitError as exc:
        return False, f"line {number}: {exc}"
    clues = sum(1 for v in values if v)
    if count != 1:
        return False, f"line {number}: {_solution_text(count)}"
    return True, f"line {number}: ok, unique solution, {clues} clues"


def cmd_batch(args):
    with open(args.file, encoding="utf-8-sig") as handle:
        text = handle.read()
    results = [_batch_line(n, raw, args.node_limit) for n, raw in core.iter_puzzle_lines(text)]
    for _, message in results:
        print(message)
    good = sum(1 for ok, _ in results if ok)
    print(f"{len(results)} puzzles: {good} ok, {len(results) - good} with problems")
    return 0 if good == len(results) else 1


def build_parser():
    parser = argparse.ArgumentParser(prog="gridsmith", description="Offline Sudoku toolkit.")
    sub = parser.add_subparsers(dest="command", required=True)

    def add(name, handler, help_text, source=True):
        p = sub.add_parser(name, help=help_text, description=help_text)
        if source:
            _add_source(p)
        p.set_defaults(handler=handler)
        return p

    add("show", cmd_show, "print a puzzle as a boxed grid with its clue count")

    add("check", cmd_check, "list rule conflicts and count solutions")

    p = add("solve", cmd_solve, "print the solution")
    p.add_argument("--oneline", action="store_true", help="print 81 characters instead of a grid")
    p.add_argument("--node-limit", type=int, default=solver.DEFAULT_NODE_LIMIT)

    p = add("count", cmd_count, "count solutions up to a limit")
    p.add_argument("--limit", type=int, default=2)
    p.add_argument("--node-limit", type=int, default=solver.DEFAULT_NODE_LIMIT)

    add("marks", cmd_marks, "show pencil marks (candidates) for every blank")

    add("rate", cmd_rate, "rate difficulty by the techniques needed")

    add("hint", cmd_hint, "explain the next step a person could take")

    p = add("verify", cmd_verify, "check a partly filled attempt against the solution")
    p.add_argument("--attempt", required=True, help="81 cells with the digits you filled in")

    p = add("generate", cmd_generate, "generate a puzzle with a unique solution", source=False)
    p.add_argument("--clues", type=int, default=generator.DEFAULT_CLUES)
    p.add_argument("--seed", type=int, help="same seed gives the same puzzle")
    p.add_argument("--oneline", action="store_true", help="print 81 characters instead of a grid")

    p = add("batch", cmd_batch, "validate every puzzle in a file, one per line", source=False)
    p.add_argument("file")
    p.add_argument("--node-limit", type=int, default=solver.DEFAULT_NODE_LIMIT)

    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        return args.handler(args)
    except ERRORS as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
