"""Backtracking search that always fills the most constrained blank first."""

from .core import CELLS, DIGITS, PEERS, conflicts

DEFAULT_NODE_LIMIT = 200_000


class SearchLimitError(RuntimeError):
    """The search visited more nodes than allowed. The puzzle is hard or the cap is too low."""


def _options(values, idx):
    used = {values[p] for p in PEERS[idx]}
    return [d for d in DIGITS if d not in used]


def search(values, limit=2, node_limit=DEFAULT_NODE_LIMIT, rng=None):
    """Find up to ``limit`` solutions. Returns (solutions, nodes visited).

    Pass ``rng`` (a random.Random) to try digits in random order, which is
    how the generator produces different full grids.
    """
    if len(values) != CELLS:
        raise ValueError(f"grid must have {CELLS} cells, found {len(values)}")
    if conflicts(values):
        return [], 0

    grid = list(values)
    solutions = []
    nodes = 0

    def fill():
        nonlocal nodes
        nodes += 1
        if nodes > node_limit:
            raise SearchLimitError(f"gave up after {node_limit} search nodes")

        best, best_options = None, None
        for idx in range(CELLS):
            if grid[idx]:
                continue
            options = _options(grid, idx)
            if best_options is None or len(options) < len(best_options):
                best, best_options = idx, options
                if len(options) <= 1:
                    break

        if best is None:
            solutions.append(list(grid))
            return len(solutions) >= limit

        if rng is not None:
            rng.shuffle(best_options)
        for digit in best_options:
            grid[best] = digit
            if fill():
                return True
        grid[best] = 0
        return False

    fill()
    return solutions, nodes


def solve(values, node_limit=DEFAULT_NODE_LIMIT):
    """Return one solution as a list of 81 ints, or None if there is none."""
    solutions, _ = search(values, limit=1, node_limit=node_limit)
    return solutions[0] if solutions else None


def count_solutions(values, limit=2, node_limit=DEFAULT_NODE_LIMIT):
    """Count solutions, stopping once ``limit`` are found."""
    solutions, _ = search(values, limit=limit, node_limit=node_limit)
    return len(solutions)
