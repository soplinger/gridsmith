"""Human-style analysis: difficulty rating, hints and checking a partly filled attempt."""

from .core import CELLS, DIGITS, UNITS, candidates, conflicts, label
from .solver import SearchLimitError, search

EASY, MEDIUM, HARD, EXPERT = "easy", "medium", "hard", "expert"
# Guessing after singles run out: at most this many search nodes counts as hard, more is expert.
HARD_NODE_LIMIT = 200


def unique_solution(values):
    """Return the only solution, or raise ValueError explaining why there isn't one."""
    problems = conflicts(values)
    if problems:
        raise ValueError("puzzle has conflicting clues: " + "; ".join(problems))
    solutions, _ = search(values, limit=2)
    if not solutions:
        raise ValueError("puzzle has no solution")
    if len(solutions) > 1:
        raise ValueError("puzzle has more than one solution")
    return solutions[0]


def _next_deduction(values):
    """First naked or hidden single as (index, digit, kind, unit text), or None.

    A naked single is a blank with only one candidate left. A hidden single is a
    digit that fits in only one blank of some row, column or box.
    """
    cand = candidates(values)
    for idx in range(CELLS):
        if not values[idx] and len(cand[idx]) == 1:
            return idx, next(iter(cand[idx])), "naked", None
    for kind, number, cells in UNITS:
        for digit in DIGITS:
            if any(values[i] == digit for i in cells):
                continue
            spots = [i for i in cells if not values[i] and digit in cand[i]]
            if len(spots) == 1:
                return spots[0], digit, "hidden", f"{kind} {number}"
    return None


def rate(values):
    """Rate a puzzle by the least human-like method that solves it.

    Returns (rating, detail). Ratings: ``easy`` needs only naked singles,
    ``medium`` needs hidden singles, ``hard`` needs a short search after singles,
    ``expert`` needs a long search.
    """
    unique_solution(values)
    grid = list(values)
    naked = hidden = 0
    while True:
        step = _next_deduction(grid)
        if step is None:
            break
        idx, digit, kind, _ = step
        grid[idx] = digit
        if kind == "naked":
            naked += 1
        else:
            hidden += 1

    nodes = 0
    if all(grid):
        rating = MEDIUM if hidden else EASY
    else:
        try:
            _, nodes = search(grid, limit=1)
            rating = HARD if nodes <= HARD_NODE_LIMIT else EXPERT
        except SearchLimitError:
            rating = EXPERT
    return rating, {"naked": naked, "hidden": hidden, "search_nodes": nodes}


def hint(values):
    """Return (index, digit, text) describing the next step a person could take."""
    solution = unique_solution(values)
    if all(values):
        raise ValueError("nothing left to fill in")

    step = _next_deduction(values)
    if step is not None:
        idx, digit, kind, unit = step
        if kind == "naked":
            text = f"{label(idx)} has only one candidate left: {digit}"
        else:
            text = f"{digit} can only go in {label(idx)} within {unit}"
        return idx, digit, text

    cand = candidates(values)
    idx = min((i for i in range(CELLS) if not values[i]), key=lambda i: len(cand[i]))
    digit = solution[idx]
    text = f"no single-step deduction is available; {label(idx)} is {digit} in the solution"
    return idx, digit, text


def check_attempt(puzzle, attempt):
    """Compare an attempt with the puzzle's unique solution.

    Returns (wrong, blanks): the indexes of filled cells with the wrong digit,
    and how many cells are still blank. Raises ValueError if the attempt
    changes or removes a given clue.
    """
    solution = unique_solution(puzzle)
    for idx in range(CELLS):
        if puzzle[idx] and attempt[idx] != puzzle[idx]:
            raise ValueError(f"attempt does not keep the given clue at {label(idx)}")
    wrong = [i for i in range(CELLS) if attempt[i] and attempt[i] != solution[i]]
    blanks = sum(1 for v in attempt if not v)
    return wrong, blanks
