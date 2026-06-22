"""Shared pytest fixtures and path setup for the Python test suite.

The LSP uses flat imports (``from command_core import ...``) and the catalog
loads ``code_aster`` from the vendored ``code_aster_version`` package, so those
directories must be importable. ``pyproject.toml`` already sets ``pythonpath``;
we also insert them here so ``pytest`` works regardless of the invocation cwd.
"""

import pathlib as pl
import sys

import pytest

_ROOT = pl.Path(__file__).resolve().parents[2]

for _candidate in (
    _ROOT / "python",
    _ROOT / "python" / "lsp",
    _ROOT / "python" / "asterstudy" / "code_aster_version",
    _ROOT / "python" / "bundled" / "libs",
):
    _s = str(_candidate)
    if _s not in sys.path:
        sys.path.insert(0, _s)


@pytest.fixture(scope="session")
def repo_root() -> pl.Path:
    return _ROOT


@pytest.fixture(scope="session")
def cata():
    """The real code_aster catalog (vendored). Loads with only numpy."""
    from asterstudy.datamodel.catalogs import CATA

    return CATA
