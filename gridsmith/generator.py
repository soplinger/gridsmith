"""Puzzle generation: a random full grid, then clues removed while the answer stays unique."""

import random

from .core import CELLS
from .solver import SearchLimitError, count_solutions, search

MIN_CLUES = 17
DEFAULT_CLUES = 30
# Uniqueness checks on sparse grids can be slow. A check that hits this cap keeps its clue.
UNIQUENESS_NODE_LIMIT = 20_000


def generate(clues=DEFAULT_CLUES, seed=None):
    """Return a puzzle (81 ints) with a unique solution and as close to ``clues`` givens as possible.

    The same seed always gives the same puzzle. Greedy removal can stop above the
    target when no further clue can go without breaking uniqueness; the caller
    should compare the returned clue count to the target.
    """
    if not MIN_CLUES <= clues <= CELLS:
        raise ValueError(f"clues must be between {MIN_CLUES} and {CELLS}")

    rng = random.Random(seed)
    full, _ = search([0] * CELLS, limit=1, rng=rng)
    puzzle = list(full[0])

    order = list(range(CELLS))
    rng.shuffle(order)
    givens = CELLS
    for idx in order:
        if givens <= clues:
            break
        backup = puzzle[idx]
        puzzle[idx] = 0
        try:
            unique = count_solutions(puzzle, limit=2, node_limit=UNIQUENESS_NODE_LIMIT) == 1
        except SearchLimitError:
            unique = False
        if unique:
            givens -= 1
        else:
            puzzle[idx] = backup
    return puzzle
