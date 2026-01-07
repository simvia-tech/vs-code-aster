# Convert a mesh stored in a .med file into a unique .obj file with multiple groups.
# Each group in the .med file is converted into a group in the .obj file.
# usage: python med2obj.py -i input.med -o .cache_dir/output.obj




import argparse
import numpy as np
import medcoupling as mc
import pathlib as pl

def parse_args():
    parser = argparse.ArgumentParser(description="Convert a .med mesh file to a .obj file with groups.")
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
    1: 1   ## Point 1 node
}

def write_obj(med_file, skin_mesh, skin_groups, node_groups, output_path, skin_level=-1, node_level=1):
    with open(output_path, 'w') as f:
        coords = skin_mesh.getCoords().toNumPyArray()
        for coord in coords:
            f.write(f"v {coord[0]} {coord[1]} {coord[2]}\n")

        for elem in skin_mesh:
            conn = elem.getAllConn()# OBJ is 1-indexed
            end_connectivity = END_CONNECTIVITY[len(conn)-1]+1
            f.write(f'f {" ".join([str(x+1) for x in conn[1:end_connectivity]])}\n')

        for group_name in skin_groups:
            submesh = med_file.getGroup(skin_level, group_name)
            f.write(f"g {group_name}\n")
            for elem in submesh:
                conn = elem.getAllConn()
                end_connectivity = END_CONNECTIVITY[len(conn)-1]+1
                f.write(f'f {" ".join([str(x+1) for x in conn[1:end_connectivity]])}\n')

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
    #med_file = med_file.quadraticToLinear()
    mesh = med_file.getMeshAtLevel(0)

    node_level = 1 
    if mesh.getMeshDimension() == 3: ## Volumic 3d mesh
        ## compute only the skin of the mesh
        skin_mesh = mesh.computeSkin()
        surface_level = -1
    else:
        skin_mesh = mesh.clone(True)
        surface_level = 0


    nodes = med_file.getGroupsOnSpecifiedLev(node_level)
    surfaces = med_file.getGroupsOnSpecifiedLev(surface_level)
    write_obj(med_file, skin_mesh, surfaces, nodes, str(output_path), skin_level=surface_level, node_level=node_level)



main()