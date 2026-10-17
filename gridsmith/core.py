"""Grid parsing, formatting and rule checks for 9x9 Sudoku.

A grid is a flat list of 81 ints, row by row. ``0`` means blank.
"""

SIZE = 9
BOX = 3
CELLS = SIZE * SIZE
DIGITS = range(1, SIZE + 1)
BLANK_CHARS = "0."


class PuzzleError(ValueError):
    """Malformed input. Carries the 1-based line and column when known."""

    def __init__(self, message, line=None, column=None):
        self.line = line
        self.column = column
        location = []
        if line is not None:
            location.append(f"line {line}")
        if column is not None:
            location.append(f"column {column}")
        prefix = ", ".join(location)
        super().__init__(f"{prefix}: {message}" if prefix else message)


def label(index):
    """Cell index 0..80 to a name such as ``r1c1``."""
    return f"r{index // SIZE + 1}c{index % SIZE + 1}"


def _build_units():
    units = []
    for r in range(SIZE):
        units.append(("row", r + 1, [r * SIZE + c for c in range(SIZE)]))
    for c in range(SIZE):
        units.append(("column", c + 1, [r * SIZE + c for r in range(SIZE)]))
    for b in range(SIZE):
        top, left = (b // BOX) * BOX, (b % BOX) * BOX
        cells = [(top + i) * SIZE + left + j for i in range(BOX) for j in range(BOX)]
        units.append(("box", b + 1, cells))
    return units


def _build_peers():
    peers = []
    for idx in range(CELLS):
        seen = set()
        for _, _, cells in UNITS:
            if idx in cells:
                seen.update(cells)
        seen.discard(idx)
        peers.append(tuple(sorted(seen)))
    return peers


# Each unit is (kind, number, cell indexes). Rows, columns, then boxes.
UNITS = _build_units()
# For each cell, the 20 other cells that share a row, column or box with it.
PEERS = _build_peers()


def parse_puzzle(text, line=None):
    """Parse one 81-cell puzzle. Whitespace is ignored; ``0`` and ``.`` mark blanks."""
    values = []
    for column, ch in enumerate(text, start=1):
        if ch.isspace():
            continue
        if ch in BLANK_CHARS:
            values.append(0)
        elif ch in "123456789":
            values.append(int(ch))
        else:
            raise PuzzleError(f"unexpected character {ch!r}", line, column)
    if len(values) != CELLS:
        raise PuzzleError(f"expected {CELLS} cells, found {len(values)}", line)
    return values


def iter_puzzle_lines(text):
    """Yield (line number, raw text) for every line that holds a puzzle.

    Blank lines and lines starting with ``#`` are skipped.
    """
    for number, raw in enumerate(text.splitlines(), start=1):
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        yield number, raw


def parse_file(text):
    """Parse every puzzle in a file. Returns [(line number, values)].

    Raises PuzzleError on the first malformed line, with its line number.
    """
    return [(number, parse_puzzle(raw, number)) for number, raw in iter_puzzle_lines(text)]


def to_line(values):
    """One-line form: 81 characters, ``.`` for blanks."""
    return "".join(str(v) if v else "." for v in values)


def format_grid(values):
    """Boxed 9x9 text grid with ``.`` for blanks."""
    separator = "------+-------+------"
    lines = []
    for r in range(SIZE):
        if r and r % BOX == 0:
            lines.append(separator)
        row = values[r * SIZE:(r + 1) * SIZE]
        cells = [str(v) if v else "." for v in row]
        groups = [" ".join(cells[i:i + BOX]) for i in range(0, SIZE, BOX)]
        lines.append(" | ".join(groups))
    return "\n".join(lines)


def conflicts(values):
    """Describe every digit that appears twice in a row, column or box."""
    problems = []
    for kind, number, cells in UNITS:
        for digit in DIGITS:
            where = [i for i in cells if values[i] == digit]
            if len(where) > 1:
                names = ", ".join(label(i) for i in where)
                problems.append(f"{kind} {number} has digit {digit} at {names}")
    return problems


def candidates(values):
    """For each cell, the digits still allowed by its peers. Filled cells give an empty set."""
    result = []
    for idx in range(CELLS):
        if values[idx]:
            result.append(set())
            continue
        used = {values[p] for p in PEERS[idx]}
        result.append({d for d in DIGITS if d not in used})
    return result
