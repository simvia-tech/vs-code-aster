# Convert a mesh stored in a .med file into a unique .obj file with multiple groups.
# Each group in the .med file is converted into a group in the .obj file.
# Supports both 3D meshes and 2D meshes (which are automatically converted to 3D).
# usage: python med2obj.py -i input.med -o .cache_dir/output.obj


import argparse
import os
import pathlib as pl
import sys

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

import medcoupling as mc  # noqa E402


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
    output_path,
    skin_level=-1,
    node_level=1,
):
    with open(output_path, "w") as f:
        coords = skin_mesh.getCoords().toNumPyArray()
        for coord in coords:
            # Ensure 2D coordinates are converted to 3D by adding z=0 if missing
            if len(coord) == 2:
                f.write(f"v {coord[0]} {coord[1]} 0.0\n")
            else:
                f.write(f"v {coord[0]} {coord[1]} {coord[2]}\n")

        for elem in skin_mesh:
            conn = elem.getAllConn()  # OBJ is 1-indexed
            end_connectivity = END_CONNECTIVITY[len(conn) - 1] + 1
            f.write(f"f {' '.join([str(x + 1) for x in conn[1:end_connectivity]])}\n")

        for group_name in skin_groups:
            submesh = med_file.getGroup(skin_level, group_name)
            f.write(f"g {group_name}\n")
            for elem in submesh:
                conn = elem.getAllConn()
                end_connectivity = END_CONNECTIVITY[len(conn) - 1] + 1
                f.write(f"f {' '.join([str(x + 1) for x in conn[1:end_connectivity]])}\n")

        for group_name in node_groups:
            node_ids = med_file.getGroupArr(node_level, group_name).toNumPyArray()
            f.write(f"ng {group_name}\n")
            for node_id in node_ids:
                f.write(f"p {node_id + 1}\n")  # OBJ is 1-indexed


def main():
    args = parse_args()
    input_path = pl.Path(args.input)
    output_path = pl.Path(args.output)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file {input_path} does not exist.")

    med_file = mc.MEDFileUMesh.New(str(input_path))
    # med_file = med_file.quadraticToLinear()
    mesh = med_file.getMeshAtLevel(0)

    node_level = 1
    if mesh.getMeshDimension() == 3:  ## Volumic 3d mesh
        ## compute only the skin of the mesh
        skin_mesh = mesh.computeSkin()
        surface_level = -1
    elif mesh.getMeshDimension() == 2:  ## 2D mesh - convert to 3D
        skin_mesh = mesh.clone(True)
        surface_level = 0
    else:  ## 1D or other - clone as is
        skin_mesh = mesh.clone(True)
        surface_level = 0

    nodes = med_file.getGroupsOnSpecifiedLev(node_level)
    surfaces = med_file.getGroupsOnSpecifiedLev(surface_level)
    write_obj(
        med_file,
        skin_mesh,
        surfaces,
        nodes,
        str(output_path),
        skin_level=surface_level,
        node_level=node_level,
    )


main()
