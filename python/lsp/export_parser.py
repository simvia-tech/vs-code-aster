"""Minimal parser for code_aster `.export` files.

The `.export` format is line-oriented. The lines we care about declare a
file bound to a logical unit::

    F mmed mesh.med   D 20
    R rmed result.rmed R 80

Token layout for file lines is ``<F|R> <type> <name> <D|DC|R|RC> <unit>``.
The 4th token encodes direction: ``D``/``DC`` = input (data), ``R``/``RC`` =
output (result). The trailing token is the logical unit number.

This mirrors the TypeScript parser in `src/ExportEditor.ts` so the report
agrees with what the form editor shows.
"""

from __future__ import annotations

from dataclasses import dataclass

DIR_IN = "in"
DIR_OUT = "out"

# Export file types that are present in essentially every study and are
# wired implicitly by code_aster rather than referenced through an explicit
# `UNITE=` in the command file. We never flag these as "declared but unused".
IMPLICIT_TYPES = {"comm", "mess"}


@dataclass
class ExportFile:
    """A single `F`/`R` file line of an `.export` file."""

    unit: int
    type: str
    name: str
    direction: str  # DIR_IN | DIR_OUT
    line: int  # 0-based line index in the .export document
    unit_col_start: int  # column of the unit token (for diagnostics)
    unit_col_end: int


def parse_export(text: str) -> list[ExportFile]:
    """Parse `.export` text into the list of declared file units.

    Lines that are not well-formed file declarations are skipped. Units that
    don't parse as integers are skipped (the form editor tolerates them too).
    """
    files: list[ExportFile] = []
    for idx, raw in enumerate(text.split("\n")):
        clean = raw.split("#", 1)[0].strip()
        if not clean:
            continue
        tokens = clean.split()
        if len(tokens) != 5 or tokens[0] not in ("F", "R"):
            continue
        _, ftype, name, io_flag, unit_str = tokens
        if io_flag in ("D", "DC"):
            direction = DIR_IN
        elif io_flag in ("R", "RC"):
            direction = DIR_OUT
        else:
            continue
        try:
            unit = int(unit_str)
        except ValueError:
            continue
        unit_col_start = raw.rfind(unit_str)
        files.append(
            ExportFile(
                unit=unit,
                type=ftype,
                name=name,
                direction=direction,
                line=idx,
                unit_col_start=unit_col_start,
                unit_col_end=unit_col_start + len(unit_str),
            )
        )
    return files
