"""Gridsmith: an offline Sudoku toolkit. Pure standard library."""

from .analysis import check_attempt, hint, rate, unique_solution
from .core import PuzzleError, candidates, conflicts, format_grid, parse_file, parse_puzzle, to_line
from .generator import generate
from .solver import SearchLimitError, count_solutions, search, solve

__version__ = "1.0.0"

__all__ = [
    "PuzzleError",
    "SearchLimitError",
    "candidates",
    "check_attempt",
    "conflicts",
    "count_solutions",
    "format_grid",
    "generate",
    "hint",
    "parse_file",
    "parse_puzzle",
    "rate",
    "search",
    "solve",
    "to_line",
    "unique_solution",
]
