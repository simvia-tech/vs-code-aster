# Extract mesh groups from a .med file, classified by topological dimension.
# Prints a JSON document to stdout: the first mesh's name, its dimension, and
# named groups bucketed into {volumes, surfaces, edges, nodes}. Consumed by the
# "Generate study from scenario" wizard to propose valid GROUP_MA / GROUP_NO
# names. Keep stdout clean (JSON only) so the TS side can JSON.parse it.
# usage: python mesh_groups.py -i input.med

import argparse
import json
import os
import pathlib as pl
import sys

# Bundled libraries (mirror python/lsp/server.py): mesh_groups.py lives at
# python/, so the shipped numpy/medcoupling are at python/bundled/libs. Prepend
# so they win over any system install.
_BUNDLED = pl.Path(__file__).parent.absolute() / "bundled" / "libs"
if str(_BUNDLED) not in sys.path:
    sys.path.insert(0, str(_BUNDLED))

# Windows DLL resolution for a system code_aster install (mirrors med2obj.py).
# No prints here — stdout must stay pure JSON.
if sys.platform == "win32" and sys.version_info >= (3, 8):
    _appdata = os.environ.get("LOCALAPPDATA", "")
    if _appdata and (pl.Path(_appdata) / "code_aster").exists():
        sys.path.append(
            rf"{_appdata}\code_aster\external\medcoupling-9.11.0\lib\python3.10\site-packages"
        )
        for _path in [
            rf"{_appdata}\code_aster\Python3.10",
            rf"{_appdata}\code_aster\external\hdf51.10.5\bin",
            rf"{_appdata}\code_aster\external\hdf51.10.5\lib",
            rf"{_appdata}\code_aster\external\MED-4.4.1\lib",
            rf"{_appdata}\code_aster\external\medcoupling-9.11.0\lib",
            rf"{_appdata}\code_aster\external\medcoupling-9.11.0\libpython3.10\site-packages",
            rf"{_appdata}\code_aster\external",
        ]:
            if os.path.isdir(_path):
                os.add_dll_directory(os.path.abspath(_path))
                sys.path.append(_path)

# Bump if the JSON schema changes in a breaking way (parallels MED2OBJ_VERSION).
MESH_GROUPS_VERSION = 1


def levels_for_dimension(dim):
    """Map a mesh dimension to the medcoupling relative levels per group kind.

    Mirrors the convention in med2obj.py. Node groups always live at level 1.
    A value of None means that kind cannot exist for this dimension.
    """
    node_level = 1
    if dim == 3:
        return {"volumes": 0, "surfaces": -1, "edges": -2, "nodes": node_level}
    if dim == 2:
        return {"volumes": None, "surfaces": 0, "edges": -1, "nodes": node_level}
    return {"volumes": None, "surfaces": None, "edges": 0, "nodes": node_level}


def build_payload(mesh_name, dim, groups_at_level):
    """Assemble the JSON payload (pure, given a `groups_at_level(level)->list`).

    `getGroupsOnSpecifiedLev` raises for an absent level, so each lookup is
    guarded and degrades to an empty list (matching extfiles.py's defensive
    handling). The node level (1) is queried directly even though it is not in
    `getNonEmptyLevels()`.
    """
    levels = levels_for_dimension(dim)

    def groups(level):
        if level is None:
            return []
        try:
            return sorted(groups_at_level(level))
        except Exception:
            return []

    return {
        "version": MESH_GROUPS_VERSION,
        "meshName": mesh_name,
        "meshDimension": dim,
        "groups": {
            "volumes": groups(levels["volumes"]),
            "surfaces": groups(levels["surfaces"]),
            "edges": groups(levels["edges"]),
            "nodes": groups(levels["nodes"]),
        },
    }


def read_mesh_groups(input_path):
    """Open a .med file with medcoupling and return the group payload."""
    import medcoupling as mc  # deferred so the pure helpers import without it

    med_file = mc.MEDFileUMesh.New(str(input_path))
    mesh = med_file.getMeshAtLevel(0)
    return build_payload(
        med_file.getName(),
        mesh.getMeshDimension(),
        med_file.getGroupsOnSpecifiedLev,
    )


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Extract .med mesh groups classified by topological dimension."
    )
    parser.add_argument("-i", "--input", type=str, required=True, help="Input .med file path.")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    input_path = pl.Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file {input_path} does not exist.")
    payload = read_mesh_groups(input_path)
    json.dump(payload, sys.stdout)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
