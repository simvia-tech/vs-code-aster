class CreateGroups {
    /**
     * Creates a CreateGroups.
     * @param {string[]} fileContext The contexts of the files to load.
     * @param {string[]} fileName The names of the files to load.
     */
    constructor(fileContexts, fileNames) {
        this.fileContexts = fileContexts;
        this.fileNames = fileNames;
        this.groups = {};
    }

    /**
     * Loads the files, creates Actors instances
     * @method
     */
    do() {

        const result = ObjLoader.loadFiles(this.fileContexts, this.fileNames);
        const post = (text) => {
        Controller.Instance.getVSCodeAPI().postMessage({
            type: 'debugPanel',
            text,
        });
        };

        if (!result) { 
            return;
        }

        const {
            vertices,
            cells,
            cellIndexToGroup,
            nodes,
            nodeIndexToGroup,
            faceGroups,
            nodeGroups,
            groupHierarchy
        } = result;

        const FaceActorCreato = new FaceActorCreator(vertices, cells, cellIndexToGroup);
        const NodeActorCreato = new NodeActorCreator(vertices, nodes, nodeIndexToGroup);

        for (const fileGroup in groupHierarchy) {
            const groupId = faceGroups.indexOf(fileGroup);

            const actor = FaceActorCreato.create(fileGroup, groupId);

            const groupInstance  = new Group(actor, fileGroup, true);

            this.groups[fileGroup] = groupInstance;

            const size = this.computeSize(actor);

            for (const faceGroup of groupHierarchy[fileGroup].faces) {
                const groupId = faceGroups.indexOf(faceGroup);

                const actor = FaceActorCreato.create(faceGroup, groupId);

                const subGroup = new Group(actor, faceGroup, true, fileGroup, size);
                this.groups[faceGroup] = subGroup;
            }

            for (const nodeGroup of groupHierarchy[fileGroup].nodes) {
                const groupId = nodeGroups.indexOf(nodeGroup);

                const actor = NodeActorCreato.create(groupId);

                const subGroup = new Group(actor, nodeGroup, false, fileGroup, size);
                this.groups[nodeGroup] = subGroup;
            }
        }

        //Reset the camera after Actors creation
        VtkApp.Instance.getRenderer().resetCamera();
        VtkApp.Instance.getRenderWindow().render();
        post(`actors : ${Object.keys(this.groups).length}`);

        //Send groups to the controller
        Controller.Instance.saveGroups(this.groups, groupHierarchy);
    }

    computeSize(actor) {
        const bounds = actor.getBounds();

        const dx = bounds[1] - bounds[0];
        const dy = bounds[3] - bounds[2];
        const dz = bounds[5] - bounds[4];

        const size = Math.sqrt(dx*dx + dy*dy + dz*dz);

        return Math.max(size, 1e-3);
    }

}   