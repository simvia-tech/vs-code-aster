# Convert a mesh stored in a .med file into a unique .obj file with multiple groups.
# Each group in the .med file is converted into a group in the .obj file.
# Supports both 3D meshes and 2D meshes (which are automatically converted to 3D).
# usage: python med2obj.py -i input.med -o .cache_dir/output.obj


import argparse
import os
import pathlib as pl
import sys

import numpy as np

python_version = sys.version_info

if sys.platform == "win32" and python_version >= (3, 8):
    # On Windows, we need to ensure that the DLLs are found, from Python 3.8 we need to
    # use os.add_dll_directory to add the directory containing the DLLs.
    # Add the directory of the current script to the DLL search path
    # This is necessary for Python 3.8+ on Windows to find the DLLs.
    # To simplify we use the LD_LIBRARY_PATH environment variable like on Unix systems.
    # ld_library_path = os.getenv("LD_LIBRARY_PATH", "")

    appdata = os.environ["LOCALAPPDATA"]

    if (pl.Path(appdata) / "code_aster").exists():
        ### Attach to code_aster windows install
        python_path = (
            rf"{appdata}\code_aster\external\medcoupling-9.11.0\lib\python3.10\site-packages"
        )
        sys.path.append(python_path)

        ld_library_path = [
            rf"{appdata}\code_aster\Python3.10",
            rf"{appdata}\code_aster\external\hdf51.10.5\bin",
            rf"{appdata}\code_aster\external\hdf51.10.5\lib",
            rf"{appdata}\code_aster\external\MED-4.4.1\lib",
            rf"{appdata}\code_aster\external\medcoupling-9.11.0\lib",
            rf"{appdata}\code_aster\external\medcoupling-9.11.0\libpython3.10\site-packages",
            rf"{appdata}\code_aster\external",
        ]

        if ld_library_path:
            # Split the LD_LIBRARY_PATH and add each directory
            for path in ld_library_path:
                print("Adding directory:", path)
                if os.path.isdir(path):
                    print(os.add_dll_directory(os.path.abspath(path)))
                    sys.path.append(path)

# Bump when the .obj output format changes in a breaking way. The extension
# reads the `# med2obj-version:` header and regenerates on mismatch.
MED2OBJ_VERSION = 4


def parse_args():
    parser = argparse.ArgumentParser(
        description="Convert a .med mesh file to a .obj file with groups."
    )
    parser.add_argument("-i", "--input", type=str, required=True, help="Input .med file path.")
    parser.add_argument("-o", "--output", type=str, required=True, help="Output .obj file path.")
    return parser.parse_args()


END_CONNECTIVITY = {
    9: 4,  ## Quadrangle 9 nodes -> Quadrangle 4 nodes
    8: 4,  ## Quadrangle 8 nodes  -> Quadrangle 4 nodes
    6: 3,  ## Triangle 6 nodes -> Triangle 3 nodes
    3: 3,  ## Triangle 3 nodes
    4: 4,  ## Quadrangle 4 nodes
    2: 2,  ## Line 2 nodes
    1: 1,  ## Point 1 node
}


def write_obj(
    med_file,
    skin_mesh,
    skin_groups,
    node_groups,
    volume_groups,
    edge_groups,
    output_path,
    skin_level=-1,
    node_level=1,
    edge_level=-2,
    n_elements=0,
    n_nodes=0,
    line_mesh=None,
    keep_nodes=None,
):
    """Write the OBJ. `keep_nodes` is a boolean mask over the mesh nodes; nodes
    outside it (referenced by no cell and no node group) are not written, so
    they cannot inflate the viewer's bounding box and camera framing."""
    coords = skin_mesh.getCoords().toNumPyArray()
    if keep_nodes is None:
        keep_nodes = np.ones(len(coords), dtype=bool)
    # 0-based MED node id -> 1-based OBJ vertex id (only valid for kept nodes).
    obj_id = np.cumsum(keep_nodes).tolist()

    def conn_str(elem):
        conn = elem.getAllConn()
        end_connectivity = END_CONNECTIVITY[len(conn) - 1] + 1
        return " ".join(str(obj_id[x]) for x in conn[1:end_connectivity])

    with open(output_path, "w") as f:
        f.write(f"# med2obj-version: {MED2OBJ_VERSION}\n")
        # True FEA counts from the full mesh (the geometry below is only the
        # rendered skin, so these can't be derived from it client-side).
        f.write(f"# elements: {n_elements}\n")
        f.write(f"# nodes: {n_nodes}\n")
        for coord in coords[keep_nodes]:
            # Ensure 2D coordinates are converted to 3D by adding z=0 if missing
            if len(coord) == 2:
                f.write(f"v {coord[0]} {coord[1]} 0.0\n")
            else:
                f.write(f"v {coord[0]} {coord[1]} {coord[2]}\n")

        for elem in skin_mesh:
            f.write(f"f {conn_str(elem)}\n")

        # 1D cells (beams) drawn as part of the object itself, before any `eg`
        # group so the viewer attaches them to the file rather than to a group.
        if line_mesh is not None:
            for elem in line_mesh:
                f.write(f"l {conn_str(elem)}\n")

        for group_name in volume_groups:
            vol_skin = med_file.getGroup(0, group_name).computeSkin()
            f.write(f"vg {group_name}\n")
            for elem in vol_skin:
                f.write(f"f {conn_str(elem)}\n")

        for group_name in skin_groups:
            submesh = med_file.getGroup(skin_level, group_name)
            f.write(f"g {group_name}\n")
            for elem in submesh:
                f.write(f"f {conn_str(elem)}\n")

        for group_name in edge_groups:
            edge_submesh = med_file.getGroup(edge_level, group_name)
            f.write(f"eg {group_name}\n")
            for elem in edge_submesh:
                f.write(f"l {conn_str(elem)}\n")

        for group_name in node_groups:
            node_ids = med_file.getGroupArr(node_level, group_name).toNumPyArray()
            f.write(f"ng {group_name}\n")
            for node_id in node_ids:
                f.write(f"p {obj_id[node_id]}\n")


def main():
    import medcoupling as mc  # deferred so the module imports without medcoupling

    args = parse_args()
    input_path = pl.Path(args.input)
    output_path = pl.Path(args.output)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file {input_path} does not exist.")

    med_file = mc.MEDFileUMesh.New(str(input_path))
    # med_file = med_file.quadraticToLinear()
    mesh = med_file.getMeshAtLevel(0)

    node_level = 1
    available_levels = set(med_file.getNonEmptyLevels())
    # code_aster counts cells of every dimension (volumes, shells, beams).
    n_elements = sum(med_file.getMeshAtLevel(lev).getNumberOfCells() for lev in available_levels)
    n_nodes = mesh.getNumberOfNodes()

    if mesh.getMeshDimension() == 3:  ## Volumic 3d mesh
        ## compute only the skin of the mesh
        skin_mesh = mesh.computeSkin()
        surface_level = -1
        edge_level = -2
        volumes = med_file.getGroupsOnSpecifiedLev(0)
        # Mixed solid/shell meshes: level -1 holds structural shells as well as
        # skin faces. Draw all of them, dropping the ones coinciding with the
        # skin (compType 2: same nodes regardless of orientation).
        if -1 in available_levels:
            skin_mesh = mc.MEDCouplingUMesh.MergeUMeshesOnSameCoords(
                [skin_mesh, med_file.getMeshAtLevel(-1)]
            )
            skin_mesh.zipConnectivityTraducer(2)
    elif mesh.getMeshDimension() == 2:  ## 2D mesh - convert to 3D
        skin_mesh = mesh.clone(True)
        surface_level = 0
        edge_level = -1
        volumes = []
    else:  ## 1D or other - clone as is
        skin_mesh = mesh.clone(True)
        surface_level = 0
        edge_level = None
        volumes = []

    line_mesh = (
        med_file.getMeshAtLevel(edge_level)
        if edge_level is not None and edge_level in available_levels
        else None
    )

    nodes = med_file.getGroupsOnSpecifiedLev(node_level)

    # Orphan nodes (no cell, no node group) are common in imported meshes and
    # can sit far from the model; keeping them would only skew the camera.
    keep_nodes = np.zeros(n_nodes, dtype=bool)
    for lev in available_levels:
        keep_nodes[med_file.getMeshAtLevel(lev).computeFetchedNodeIds().toNumPyArray()] = True
    for group_name in nodes:
        keep_nodes[med_file.getGroupArr(node_level, group_name).toNumPyArray()] = True

    surfaces = med_file.getGroupsOnSpecifiedLev(surface_level)
    edges = (
        med_file.getGroupsOnSpecifiedLev(edge_level)
        if edge_level is not None and edge_level in available_levels
        else []
    )
    write_obj(
        med_file,
        skin_mesh,
        surfaces,
        nodes,
        volumes,
        edges,
        str(output_path),
        skin_level=surface_level,
        node_level=node_level,
        edge_level=edge_level if edge_level is not None else -2,
        n_elements=n_elements,
        n_nodes=n_nodes,
        line_mesh=line_mesh,
        keep_nodes=keep_nodes,
    )


if __name__ == "__main__":
    main()
