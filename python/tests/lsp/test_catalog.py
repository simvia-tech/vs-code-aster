"""Smoke tests for the vendored code_aster catalog (CATA)."""

import pytest

SCENARIO_COMMANDS = [
    "MECA_STATIQUE",
    "STAT_NON_LINE",
    "CALC_MODES",
    "AFFE_CARA_ELEM",
    "DEFI_MATERIAU",
    "AFFE_MODELE",
    "LIRE_MAILLAGE",
    "IMPR_RESU",
]


def test_catalog_loads_commands(cata):
    assert len(cata.get_commands()) > 100


@pytest.mark.parametrize("name", SCENARIO_COMMANDS)
def test_scenario_commands_exist(cata, name):
    assert cata.get_command_obj(name) is not None


def test_meca_statique_has_expected_keywords(cata):
    parsed = cata.parse_command(cata.get_command_obj("MECA_STATIQUE"))
    top_level = {p["name"] for p in parsed["params"]}
    assert "MODELE" in top_level
    assert "CHAM_MATER" in top_level
    assert "CARA_ELEM" in top_level


def test_affe_cara_elem_supports_shell_and_beam(cata):
    parsed = cata.parse_command(cata.get_command_obj("AFFE_CARA_ELEM"))
    top_level = {p["name"] for p in parsed["params"]}
    assert "COQUE" in top_level
    assert "POUTRE" in top_level
