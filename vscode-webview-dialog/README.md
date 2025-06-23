# VS Code Webview Dialog Proof of Concept

## Contents
This repo contains a library project `vscode-webview-dialog` and a test/demo VS Code extension project `vscode-webview-dialog-test` that references the library.

## Development instructions
1. Open the repo root directory in VS Code.
2. Run `yarn` at the root.
3. Press F5 to launch the test extension in a new VS Code window.
4. Use the command palette to invoke the command: `WebView Dialog Test: Show Dialog`

The test extension uses the `WebviewDialog` class in the library to create a simple dialog. The dialog loads CSS and script from separate files in a secure way (with a CSP). The script communicates with the main extension via messages: sending result or cancellation actions.
