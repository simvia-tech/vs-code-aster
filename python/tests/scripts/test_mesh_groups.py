"""Tests for python/mesh_groups.py — pure payload shaping plus a
medcoupling-gated read of the committed cube.med fixture.
"""

import pathlib as pl

import mesh_groups
import pytest

CUBE = pl.Path(__file__).resolve().parents[1] / "fixtures" / "meshes" / "cube.med"


def test_levels_for_dimension():
    assert mesh_groups.levels_for_dimension(3) == {
        "volumes": 0,
        "surfaces": -1,
        "edges": -2,
        "nodes": 1,
    }
    assert mesh_groups.levels_for_dimension(2) == {
        "volumes": None,
        "surfaces": 0,
        "edges": -1,
        "nodes": 1,
    }
    assert mesh_groups.levels_for_dimension(1) == {
        "volumes": None,
        "surfaces": None,
        "edges": 0,
        "nodes": 1,
    }


def test_build_payload_sorts_and_guards_empty_levels():
    data = {0: ["SOLID"], -1: ["TOP", "BOTTOM"], 1: ["SUPPORT"]}

    def groups_at_level(level):
        if level not in data:
            raise RuntimeError("empty level")  # medcoupling raises here
        return data[level]

    payload = mesh_groups.build_payload("M", 3, groups_at_level)
    assert payload["version"] == 1
    assert payload["meshName"] == "M"
    assert payload["meshDimension"] == 3
    assert payload["groups"]["volumes"] == ["SOLID"]
    assert payload["groups"]["surfaces"] == ["BOTTOM", "TOP"]  # sorted
    assert payload["groups"]["edges"] == []  # raised -> guarded to []
    assert payload["groups"]["nodes"] == ["SUPPORT"]


@pytest.mark.skipif(not CUBE.exists(), reason="cube.med fixture missing")
def test_read_real_mesh():
    pytest.importorskip("medcoupling")
    payload = mesh_groups.read_mesh_groups(str(CUBE))
    assert payload["meshDimension"] == 3
    assert payload["groups"]["volumes"] == ["SOLID"]
    assert payload["groups"]["surfaces"] == ["BOTTOM", "TOP"]
    assert payload["groups"]["nodes"] == ["SUPPORT"]
    assert payload["groups"]["edges"] == []
