/**
 * Loads OBJ-like file contents and constructs geometry data structures.
 * Handles vertices, faces, nodes, face groups, node groups, and group hierarchy.
 */
class ObjLoader {

    /**
     * Parses file contents and returns structured geometry info.
     * @param {string[]} fileContexts - Array of file contents (one string per file)
     * @param {string[]} fileNames - Corresponding names of the files
     * @returns {Object} - Geometry data including vertices, cells, nodes, and group mappings
     */
    static loadFiles(fileContexts, fileNames) {
        
        const vertices = [],
            cells = [],
            cellIndexToGroup = [],
            nodes = [],
            nodeIndexToGroup = [],
            faceGroups = [],
            nodeGroups = [],
            groupHierarchy = {};
        
        let nbVertices = 0;
        let groupId = -1; 
        let nodeGroupId = -1;

        for (let i = 0; i < fileContexts.length; i++) {
            try {
                groupId++;
                const skinName = "all_" + fileNames[i];
                
                groupHierarchy[skinName] = { faces: [], nodes: [] };
                faceGroups.push(skinName);
                nbVertices = vertices.length;

                // Split lines and normalize line endings
                const lines = fileContexts[i].split('\n').map(l => l.replace('\r', ''));

                let vertexCount = 0;
                let faceCount = 0;

                for (let lineIdx = 0; lineIdx < lines.length; lineIdx++) {
                    const line = lines[lineIdx];
                    const ss = line.split(' ').filter(p => p.length !== 0);
                    if (ss.length === 0) { continue; }

                    switch (ss[0]) {
                        case 'v': // Vertex definition
                            vertices.push({
                                x: Number.parseFloat(ss[1]),
                                y: Number.parseFloat(ss[2]),
                                z: Number.parseFloat(ss[3])
                            });
                            vertexCount++;
                            break;

                        case 'f': // Face definition
                            const faceIndices = ss.slice(1).map(p => Number.parseInt(p) - 1 + nbVertices);
                            cells.push(faceIndices);
                            cellIndexToGroup.push(groupId);
                            faceCount++;
                            break;

                        case 'g': // New face group
                            groupId++;
                            const faceGroupName = ss[1] || `group${groupId}`;
                            faceGroups.push(faceGroupName);
                            groupHierarchy[skinName].faces.push(faceGroupName);
                            break;

                        case 'ng': // New node group
                            nodeGroupId++;
                            const nodeGroupName = ss[1] || `nodeGroup${nodeGroupId}`;
                            nodeGroups.push(nodeGroupName);
                            groupHierarchy[skinName].nodes.push(nodeGroupName);
                            break;

                        case 'p': // Node assignment
                            const nodeIndex = parseInt(ss[1]);
                            nodes.push(nodeIndex - 1 + nbVertices);
                            nodeIndexToGroup.push(nodeGroupId);
                            break;
                    }
                }
                
            } catch (fileError) {
                Controller.Instance.getVSCodeAPI().postMessage({
                    type: 'debugPanel',
                    text: `ERROR: ${fileError.message}`
                });
                throw fileError;
            }
        }

        Controller.Instance.getVSCodeAPI().postMessage({
            type: 'debugPanel',
            text: `TOTAL: ${vertices.length} vertices, ${cells.length} cells, ${nodes.length} nodes`
        });

        return {
            vertices,
            cells,
            cellIndexToGroup,
            nodes,
            nodeIndexToGroup,
            faceGroups,
            nodeGroups,
            groupHierarchy
        };
    }
}
