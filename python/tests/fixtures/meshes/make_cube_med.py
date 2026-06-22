"""Regenerate the tiny `cube.med` test fixture.

Local-only helper — run it by hand on a machine that has `medcoupling`
installed (it is never run in CI). Produces a single-hexahedron 3D mesh with a
volume group (SOLID), two face groups (BOTTOM, TOP) and a node group
(SUPPORT), which is enough to exercise the mesh-group readers.

usage: python make_cube_med.py
"""

import pathlib as pl

import medcoupling as mc

OUT = pl.Path(__file__).with_name("cube.med")


def build() -> mc.MEDFileUMesh:
    coords = [
        [0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        [1.0, 1.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0],
        [1.0, 0.0, 1.0],
        [1.0, 1.0, 1.0],
        [0.0, 1.0, 1.0],
    ]
    coo = mc.DataArrayDouble(coords)

    volume = mc.MEDCouplingUMesh("cube", 3)
    volume.setCoords(coo)
    volume.allocateCells(1)
    volume.insertNextCell(mc.NORM_HEXA8, [0, 1, 2, 3, 4, 5, 6, 7])
    volume.finishInsertingCells()

    faces = mc.MEDCouplingUMesh("cube", 2)
    faces.setCoords(coo)
    faces.allocateCells(2)
    faces.insertNextCell(mc.NORM_QUAD4, [0, 1, 2, 3])  # bottom (z = 0)
    faces.insertNextCell(mc.NORM_QUAD4, [4, 5, 6, 7])  # top (z = 1)
    faces.finishInsertingCells()

    mesh = mc.MEDFileUMesh()
    mesh.setMeshAtLevel(0, volume)
    mesh.setMeshAtLevel(-1, faces)

    solid = mc.DataArrayInt([0])
    solid.setName("SOLID")
    mesh.setGroupsAtLevel(0, [solid])

    bottom = mc.DataArrayInt([0])
    bottom.setName("BOTTOM")
    top = mc.DataArrayInt([1])
    top.setName("TOP")
    mesh.setGroupsAtLevel(-1, [bottom, top])

    support = mc.DataArrayInt([0, 1, 2, 3])
    support.setName("SUPPORT")
    mesh.setGroupsAtLevel(1, [support])

    return mesh


def main() -> None:
    mesh = build()
    mesh.write(str(OUT), 2)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
