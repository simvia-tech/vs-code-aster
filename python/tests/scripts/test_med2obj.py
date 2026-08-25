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
    assert "# elements: 3" in text  # one hexahedron + two skin faces (BOTTOM, TOP)
    assert "# nodes: 8" in text
    assert "vg SOLID" in text  # volume group marker
    # BOTTOM/TOP coincide with the skin: no duplicate faces in the object.
    object_faces = text.split("\nvg ", 1)[0].count("\nf ")
    assert object_faces == 6


def _object_section(text: str) -> str:
    """Lines drawn as the object itself: everything before the first group marker."""
    for marker in ("\nvg ", "\ng ", "\neg ", "\nng "):
        text = text.split(marker, 1)[0]
    return text


def test_mixed_solid_shell_beam_mesh_is_drawn_whole(tmp_path, monkeypatch):
    """Shells and beams below the volume level must be part of the object, not
    only reachable through groups (a body-in-white with a solid part)."""
    mc = pytest.importorskip("medcoupling")
    coo = mc.DataArrayDouble(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [1.0, 1.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
            [1.0, 0.0, 1.0],
            [1.0, 1.0, 1.0],
            [0.0, 1.0, 1.0],
            [2.0, 0.0, 0.0],  # detached shell + beam, not touching the cube
            [3.0, 0.0, 0.0],
            [3.0, 1.0, 0.0],
            [2.0, 1.0, 0.0],
            [4.0, 0.0, 0.0],
            [90.0, 90.0, 90.0],  # orphan: no cell, no group -> dropped
            [5.0, 0.0, 0.0],  # orphan but in a node group (RBE3 master) -> kept
        ]
    )
    volume = mc.MEDCouplingUMesh("m", 3)
    volume.setCoords(coo)
    volume.allocateCells(1)
    volume.insertNextCell(mc.NORM_HEXA8, [0, 1, 2, 3, 4, 5, 6, 7])
    volume.finishInsertingCells()

    faces = mc.MEDCouplingUMesh("m", 2)
    faces.setCoords(coo)
    faces.allocateCells(2)
    faces.insertNextCell(mc.NORM_QUAD4, [0, 3, 2, 1])  # cube bottom, reversed orientation
    faces.insertNextCell(mc.NORM_QUAD4, [8, 9, 10, 11])  # structural shell
    faces.finishInsertingCells()

    beams = mc.MEDCouplingUMesh("m", 1)
    beams.setCoords(coo)
    beams.allocateCells(2)
    beams.insertNextCell(mc.NORM_SEG2, [9, 12])  # ungrouped beam
    beams.insertNextCell(mc.NORM_SEG2, [0, 1])  # coincides with a cube edge
    beams.finishInsertingCells()

    mesh = mc.MEDFileUMesh()
    mesh.setMeshAtLevel(0, volume)
    mesh.setMeshAtLevel(-1, faces)
    mesh.setMeshAtLevel(-2, beams)
    master = mc.DataArrayInt([14])
    master.setName("MASTER")
    mesh.setGroupsAtLevel(1, [master])
    med = tmp_path / "mixed.med"
    mesh.write(str(med), 2)

    out = tmp_path / "mixed.obj"
    monkeypatch.setattr(sys, "argv", ["med2obj.py", "-i", str(med), "-o", str(out)])
    med2obj.main()
    text = out.read_text()

    assert "# elements: 5" in text  # 1 hexa + 2 faces + 2 beams
    assert "# nodes: 15" in text  # FEA count keeps every node of the file
    obj = _object_section(text)
    assert obj.count("\nf ") == 7  # 6 skin faces (bottom deduped) + 1 shell
    assert obj.count("\nl ") == 2  # every 1D cell; the viewer hides those lying on faces
    assert "\neg " not in text and "\ng " not in text  # nothing was grouped
    # Orphan node 13 is dropped and later ids are shifted; node 14 survives via its group.
    assert obj.count("\nv ") == 14
    assert "v 90.0 90.0 90.0" not in text
    assert "ng MASTER\np 14\n" in text
    assert "\nl 10 13\n" in obj  # beam [9, 12] -> 1-based, unshifted (before the orphan)
