"""Unit tests for the pure catalog-validation helpers in lsp/validators.py."""

from validators import (
    expected_classes,
    find_keyword,
    find_param,
    is_bare_identifier,
    required_keywords,
    simp_defaults,
    types_compatible,
    value_in_into,
    visible_keywords,
)


# Fakes mirroring the CATA kwd object shape: _is_factor / _is_bloc key off the
# class name containing "FactorKeyword" / "Bloc", and every kwd has .definition.
class FakeSimp:
    def __init__(self, **definition):
        self.definition = definition


class FakeFactorKeyword:
    def __init__(self, definition):
        self.definition = definition


class FakeBloc:
    def __init__(self, definition, enabled=True):
        self.definition = definition
        self._enabled = enabled

    def isEnabled(self, _context):
        return self._enabled


class TestValueInInto:
    def test_plain_string_match(self):
        assert value_in_into("3D", ("3D", "D_PLAN")) is True

    def test_quoted_source_matches_unquoted_entry(self):
        assert value_in_into('"3D"', ("3D",)) is True
        assert value_in_into("'D_PLAN'", ("D_PLAN",)) is True

    def test_numeric_match(self):
        assert value_in_into("1", (1, 2, 3)) is True
        assert value_in_into("1.0", (1,)) is True

    def test_no_match_and_empty(self):
        assert value_in_into("NOPE", ("3D",)) is False
        assert value_in_into("", ("3D",)) is False
        assert value_in_into("3D", ()) is False


class TestIsBareIdentifier:
    def test_identifiers(self):
        assert is_bare_identifier("mesh") is True
        assert is_bare_identifier("element_properties") is True

    def test_non_identifiers(self):
        assert is_bare_identifier('"text"') is False
        assert is_bare_identifier("42") is False
        assert is_bare_identifier("3.14") is False
        assert is_bare_identifier("None") is False
        assert is_bare_identifier("") is False


class TestTypesCompatible:
    def test_subclass_match(self):
        class A:
            pass

        class B(A):
            pass

        assert types_compatible((B,), (A,)) is True
        assert types_compatible((A,), (B,)) is False

    def test_empty_inputs(self):
        assert types_compatible((), (int,)) is False
        assert types_compatible((int,), ()) is False


class TestExpectedClasses:
    def test_parsed_param_dict(self):
        assert expected_classes({"type_obj": int}) == (int,)

    def test_string_tag_returns_empty(self):
        assert expected_classes({"type_obj": "R"}) == ()
        assert expected_classes({"type_obj": None}) == ()


class TestFindParam:
    def test_top_level(self):
        params = [{"name": "MODELE"}, {"name": "CHAM_MATER"}]
        assert find_param(params, "MODELE")["name"] == "MODELE"
        assert find_param(params, "MISSING") is None

    def test_descends_into_bloc_children(self):
        params = [
            {"name": "PHENOMENE"},
            {
                "name": "b_meca",
                "bloc": True,
                "children": [{"name": "MODELISATION"}],
            },
        ]
        assert find_param(params, "MODELISATION")["name"] == "MODELISATION"


class TestKeywordTreeHelpers:
    def _definition(self):
        return {
            "MODELE": FakeSimp(statut="o", typ="R"),
            "ELAS": FakeFactorKeyword({"E": FakeSimp(statut="o", typ="R")}),
            "b_on": FakeBloc({"COQUE": FakeSimp(statut="f", typ="R")}, enabled=True),
            "b_off": FakeBloc({"HIDDEN": FakeSimp(statut="o", typ="R")}, enabled=False),
        }

    def test_find_keyword_descends_factor(self):
        defn = self._definition()
        assert find_keyword(defn, "E", None) is not None
        assert find_keyword(defn, "MODELE", None) is not None
        assert find_keyword(defn, "NOPE", None) is None

    def test_find_keyword_skips_disabled_bloc_with_context(self):
        defn = self._definition()
        # With a context, the disabled bloc's child is not reachable.
        assert find_keyword(defn, "HIDDEN", {"x": 1}) is None
        # The enabled bloc's child is reachable.
        assert find_keyword(defn, "COQUE", {"x": 1}) is not None

    def test_visible_keywords_filters_disabled_blocs(self):
        defn = self._definition()
        names = {n for n, _ in visible_keywords(defn, {"x": 1})}
        assert "MODELE" in names
        assert "COQUE" in names
        assert "HIDDEN" not in names

    def test_required_keywords(self):
        defn = self._definition()
        required = set(required_keywords(defn, {"x": 1}))
        assert "MODELE" in required
        assert "COQUE" not in required  # statut "f"

    def test_simp_defaults(self):
        defn = {
            "OPTION": FakeSimp(statut="f", typ="TXM", defaut="PLUS_PETITE"),
            "MODELE": FakeSimp(statut="o", typ="R"),
        }
        assert simp_defaults(defn) == {"OPTION": "PLUS_PETITE"}
