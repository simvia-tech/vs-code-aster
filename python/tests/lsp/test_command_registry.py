"""Tests for the .comm command parser (lsp/command_registry.py).

Parsing is pure: ``initialize`` only stores the passed ``ls`` reference and
otherwise works on the raw lines, so we pass ``None`` for ``ls``.
"""

from command_registry import CommandRegistry


def build(text: str) -> CommandRegistry:
    reg = CommandRegistry()
    reg.initialize(None, text.split("\n"))
    return reg


def names(reg: CommandRegistry) -> list[str]:
    return [c.name for c in reg.commands.values()]


def test_single_line_command_with_assignment():
    reg = build('mesh = LIRE_MAILLAGE(FORMAT="MED", UNITE=20)')
    cmd = next(iter(reg.commands.values()))
    assert cmd.name == "LIRE_MAILLAGE"
    assert cmd.var_name == "mesh"
    assert cmd.is_complete is True
    assert cmd.parsed_params["FORMAT"] == "MED"
    assert cmd.parsed_params["UNITE"] == "20"


def test_multiline_command_with_factor_keyword():
    text = "\n".join(
        [
            "model = AFFE_MODELE(",
            "    MAILLAGE=mesh,",
            '    AFFE=_F(TOUT="OUI", PHENOMENE="MECANIQUE", MODELISATION="3D"),',
            ")",
        ]
    )
    reg = build(text)
    cmd = next(iter(reg.commands.values()))
    assert cmd.name == "AFFE_MODELE"
    assert cmd.is_complete is True
    assert cmd.parsed_params["MAILLAGE"] == "mesh"
    # The _F(...) value is collapsed and its inner keywords are not top-level.
    assert cmd.parsed_params["AFFE"] == "_F(...)"
    assert "PHENOMENE" not in cmd.parsed_params


def test_factor_keyword_open_paren_is_not_a_command():
    # `_F(` must not be detected as a command start (negative lookahead).
    text = "\n".join(
        [
            "load = AFFE_CHAR_MECA(",
            '    PRES_REP=_F(GROUP_MA=("TOP",), PRES=1.0),',
            ")",
        ]
    )
    reg = build(text)
    assert names(reg) == ["AFFE_CHAR_MECA"]


def test_comment_and_inline_comment_handling():
    text = "\n".join(
        [
            "# a comment",
            "mesh = LIRE_MAILLAGE(UNITE=20)  # inline comment with ) paren",
            "# DEBUT(should be ignored)",
        ]
    )
    reg = build(text)
    assert names(reg) == ["LIRE_MAILLAGE"]


def test_string_with_parentheses_does_not_break_matching():
    reg = build('x = DEFI_FONCTION(NOM_PARA="INST")')
    cmd = next(iter(reg.commands.values()))
    assert cmd.is_complete is True
    assert cmd.parsed_params["NOM_PARA"] == "INST"


def test_incomplete_command_marked_not_complete():
    reg = build("result = MECA_STATIQUE(\n    MODELE=model,")
    cmd = next(iter(reg.commands.values()))
    assert cmd.name == "MECA_STATIQUE"
    assert cmd.is_complete is False


def test_multiple_commands_and_get_all():
    text = "\n".join(
        [
            "mesh = LIRE_MAILLAGE(UNITE=20)",
            "model = AFFE_MODELE(MAILLAGE=mesh)",
            "FIN()",
        ]
    )
    reg = build(text)
    assert set(names(reg)) == {"LIRE_MAILLAGE", "AFFE_MODELE", "FIN"}
    assert len(reg.get_all_commands()) == 3


def test_parse_keyword_positions_top_level_only():
    text = "\n".join(
        [
            "result = MECA_STATIQUE(",
            "    MODELE=model,",
            "    CHAM_MATER=material_field,",
            ")",
        ]
    )
    reg = build(text)
    cmd = next(iter(reg.commands.values()))
    positions = reg.parse_keyword_positions(text.split("\n"), cmd)
    kw = {p.name for p in positions}
    assert "MODELE" in kw
    assert "CHAM_MATER" in kw
