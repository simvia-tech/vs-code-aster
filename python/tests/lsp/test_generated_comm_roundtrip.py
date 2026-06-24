"""Cross-layer contract: the .comm files emitted by the TypeScript scenario
generator must parse cleanly under the real code_aster catalog.

For every golden study (src/scenario/fixtures/<case>/expected.comm) every
detected command must be a real CATA command and every top-level keyword must
be a known keyword of that command. This ties the wizard's output to the
catalog without duplicating the generator in Python; a drift fails here.
"""

import pathlib as pl

from command_registry import CommandRegistry
from validators import find_param


def _golden_comms(root: pl.Path):
    fixtures = root / "src" / "scenario" / "fixtures"
    return sorted(fixtures.glob("*/expected.comm"))


def _case_id(path: pl.Path) -> str:
    return path.parent.name


def test_goldens_present(repo_root):
    assert len(_golden_comms(repo_root)) >= 5


def pytest_generate_tests(metafunc):
    if "golden_comm" in metafunc.fixturenames:
        root = pl.Path(__file__).resolve().parents[3]
        comms = _golden_comms(root)
        metafunc.parametrize("golden_comm", comms, ids=[_case_id(p) for p in comms])


def test_generated_comm_is_catalog_valid(golden_comm, cata):
    lines = golden_comm.read_text().split("\n")
    registry = CommandRegistry()
    registry.initialize(None, lines)

    problems: list[str] = []
    for cmd in registry.commands.values():
        obj = cata.get_command_obj(cmd.name)
        if obj is None:
            problems.append(f"unknown command: {cmd.name}")
            continue
        parsed = cata.parse_command(obj)
        params = parsed.get("params", [])
        for keyword in cmd.parsed_params:
            if find_param(params, keyword) is None:
                problems.append(f"{cmd.name}: unknown keyword {keyword}")

    assert not problems, "\n".join(problems)
