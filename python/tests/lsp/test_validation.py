"""Tests for whole-study validation (lsp/managers/validation_manager.py).

Covers the Definition-of-Done matrix: a valid study, an undefined concept, an
unused concept, and the three I/O cross-check cases (unit used in .comm but
missing from .export, unit declared in .export but unused in .comm, and an
input/output direction mismatch).
"""

from export_parser import DIR_IN, DIR_OUT, parse_export
from validation_manager import ValidationManager

VALID_COMM = "\n".join(
    [
        "DEBUT()",
        "mesh = LIRE_MAILLAGE(UNITE=20, FORMAT='MED')",
        "model = AFFE_MODELE(MAILLAGE=mesh,",
        "    AFFE=_F(TOUT='OUI', PHENOMENE='MECANIQUE', MODELISATION='3D'))",
        "mater = DEFI_MATERIAU(ELAS=_F(E=210000.0, NU=0.3))",
        "fieldmat = AFFE_MATERIAU(MAILLAGE=mesh, AFFE=_F(TOUT='OUI', MATER=mater))",
        "bc = AFFE_CHAR_MECA(MODELE=model, DDL_IMPO=_F(GROUP_NO='fix', DX=0.0))",
        "res = MECA_STATIQUE(MODELE=model, CHAM_MATER=fieldmat, EXCIT=_F(CHARGE=bc))",
        "IMPR_RESU(UNITE=80, FORMAT='MED', RESU=_F(RESULTAT=res))",
        "FIN()",
    ]
)

VALID_EXPORT = "\n".join(
    [
        "P actions make_etude",
        "F comm case.comm D 1",
        "F mmed mesh.med D 20",
        "F mess case.mess R 6",
        "F rmed result.rmed R 80",
    ]
)


def _mgr() -> ValidationManager:
    return ValidationManager()


def _row(report, command):
    return next(r for r in report["commands"] if r["command"] == command)


def _codes(report):
    return {d["code"] for d in report["diagnostics"]}


# --------------------------------------------------------------- export parser


def test_export_parser_directions_and_units():
    files = parse_export(VALID_EXPORT)
    by_unit = {f.unit: f for f in files}
    assert by_unit[20].direction == DIR_IN
    assert by_unit[20].type == "mmed"
    assert by_unit[80].direction == DIR_OUT
    assert by_unit[1].type == "comm"


# --------------------------------------------------------------- valid study


def test_valid_study_has_no_diagnostics():
    report = _mgr().validate_study(VALID_COMM, VALID_EXPORT)
    assert report["diagnostics"] == [], report["diagnostics"]

    lire = _row(report, "LIRE_MAILLAGE")
    assert lire["concept"] == "mesh"
    assert lire["syntactic"] and lire["dependency"] and lire["naming"]
    assert lire["used"] is True

    # Commands that don't produce a concept are "not applicable" for Used.
    assert _row(report, "IMPR_RESU")["used"] is None
    assert _row(report, "FIN")["used"] is None


def test_valid_study_io_all_consistent():
    report = _mgr().validate_study(VALID_COMM, VALID_EXPORT)
    io = {r["unit"]: r for r in report["io"]}
    assert io[20]["status"] == "ok"
    assert io[20]["direction"] == "Input"
    assert io[80]["status"] == "ok"
    assert io[80]["direction"] == "Output"
    # comm / mess units are implicit, never flagged as unused.
    assert io[1]["status"] == "ok"
    assert io[1]["usedIn"] == "implicit"


# --------------------------------------------------------- command/concept


def test_undefined_concept_reported():
    comm = "\n".join(
        [
            "model = AFFE_MODELE(MAILLAGE=mesh,",
            "    AFFE=_F(TOUT='OUI', PHENOMENE='MECANIQUE', MODELISATION='3D'))",
            "FIN()",
        ]
    )
    report = _mgr().validate_study(comm, "")
    affe = _row(report, "AFFE_MODELE")
    assert affe["dependency"] is False
    assert "dependency" in _codes(report)
    dep = next(d for d in report["diagnostics"] if d["code"] == "dependency")
    assert "mesh" in dep["message"]
    assert dep["file"] == "comm"


def test_unused_concept_reported():
    comm = "\n".join(
        [
            "mesh = LIRE_MAILLAGE(UNITE=20, FORMAT='MED')",
            "mater = DEFI_MATERIAU(ELAS=_F(E=210000.0, NU=0.3))",
            "FIN()",
        ]
    )
    report = _mgr().validate_study(comm, "")
    mater = _row(report, "DEFI_MATERIAU")
    assert mater["used"] is False
    unused = [d for d in report["diagnostics"] if d["code"] == "unused"]
    assert any("mater" in d["message"] for d in unused)


# ------------------------------------------------------------------- I/O


def test_unit_used_in_comm_missing_from_export():
    comm = "\n".join(
        [
            "mesh = LIRE_MAILLAGE(UNITE=20, FORMAT='MED')",
            "tab = LIRE_TABLE(UNITE=33)",
            "FIN()",
        ]
    )
    export = "\n".join(["F comm case.comm D 1", "F mmed mesh.med D 20"])
    report = _mgr().validate_study(comm, export)
    assert "io-missing-export" in _codes(report)
    miss = next(d for d in report["diagnostics"] if d["code"] == "io-missing-export")
    assert "33" in miss["message"]
    io = {r["unit"]: r for r in report["io"]}
    assert io[33]["status"] == "error"


def test_unit_declared_in_export_unused_in_comm():
    comm = "\n".join(["mesh = LIRE_MAILLAGE(UNITE=20, FORMAT='MED')", "FIN()"])
    export = "\n".join(
        [
            "F comm case.comm D 1",
            "F mmed mesh.med D 20",
            "F mmed extra.med D 21",
        ]
    )
    report = _mgr().validate_study(comm, export)
    assert "io-unused-export" in _codes(report)
    unused = next(d for d in report["diagnostics"] if d["code"] == "io-unused-export")
    assert "21" in unused["message"]
    io = {r["unit"]: r for r in report["io"]}
    assert io[21]["status"] == "warning"
    assert io[21]["usedIn"] == "—"


def test_unit_zero_declared_in_export_not_flagged():
    comm = "\n".join(["mesh = LIRE_MAILLAGE(UNITE=20, FORMAT='MED')", "FIN()"])
    export = "\n".join(
        [
            "F comm case.comm D 1",
            "F mmed mesh.med D 20",
            "F repe results R 0",
        ]
    )
    report = _mgr().validate_study(comm, export)
    assert "io-unused-export" not in _codes(report)
    io = {r["unit"]: r for r in report["io"]}
    assert io[0]["status"] == "ok"
    assert io[0]["usedIn"] == "implicit"


def test_input_output_direction_mismatch():
    comm = "\n".join(["mesh = LIRE_MAILLAGE(UNITE=20, FORMAT='MED')", "FIN()"])
    export = "\n".join(["F comm case.comm D 1", "F rmed result.rmed R 20"])
    report = _mgr().validate_study(comm, export)
    assert "io-direction" in _codes(report)
    mism = next(d for d in report["diagnostics"] if d["code"] == "io-direction")
    assert "20" in mism["message"]
    io = {r["unit"]: r for r in report["io"]}
    assert io[20]["status"] == "error"
