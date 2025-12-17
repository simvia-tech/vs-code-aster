// Entry point for the VS Code Webview
const vscode = acquireVsCodeApi(); // VS Code API for messaging with the extension
const scene = document.getElementById("scene"); // HTML scene for rendering
Controller.Instance.init(scene, vscode); // Initialize the main Controller with scene and VS Code API

// Listen for messages from the extension
window.addEventListener("message", async (e) => {
  const { type, body } = e.data;

  switch (type) {
    // Initialize the visualization with loaded OBJ files
    case "init":
      Controller.Instance.loadFiles(body.fileContexts, body.objFilenames);
      break;

    // Toggle visibility for a specific group and update the UI label
    case "displayGroup":
      VisibilityManager.Instance.setVisibility(body.group, body.visible);
      break;
  }
});

// Notify the extension that the webview is ready
vscode.postMessage({ type: "ready" });
