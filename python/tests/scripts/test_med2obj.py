"""Tests for python/med2obj.py — pure helpers plus a medcoupling-gated
conversion of the committed cube.med fixture.
"""

import pathlib as pl
import sys

import med2obj
import pytest

CUBE = pl.Path(__file__).resolve().parents[1] / "fixtures" / "meshes" / "cube.med"


def test_parse_args(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["med2obj.py", "-i", "in.med", "-o", "out.obj"])
    args = med2obj.parse_args()
    assert args.input == "in.med"
    assert args.output == "out.obj"


def test_end_connectivity_map():
    assert med2obj.END_CONNECTIVITY[8] == 4  # quad8 -> quad4
    assert med2obj.END_CONNECTIVITY[6] == 3  # tri6 -> tri3
    assert med2obj.END_CONNECTIVITY[2] == 2  # line2


@pytest.mark.skipif(not CUBE.exists(), reason="cube.med fixture missing")
def test_main_writes_obj_with_counts_and_groups(tmp_path, monkeypatch):
    pytest.importorskip("medcoupling")
    out = tmp_path / "cube.obj"
    monkeypatch.setattr(sys, "argv", ["med2obj.py", "-i", str(CUBE), "-o", str(out)])
    med2obj.main()
    text = out.read_text()
    assert f"# med2obj-version: {med2obj.MED2OBJ_VERSION}" in text
    assert "# elements: 1" in text  # one hexahedron at level 0
    assert "# nodes: 8" in text
    assert "vg SOLID" in text  # volume group marker
