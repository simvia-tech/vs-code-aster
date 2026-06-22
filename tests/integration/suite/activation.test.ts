import * as assert from 'assert';
import * as vscode from 'vscode';

const EXTENSION_ID = 'simvia.vs-code-aster';

const CONTRIBUTED_COMMANDS = [
  'vs-code-aster.run-aster',
  'vs-code-aster.exportDoc',
  'vs-code-aster.meshViewer',
  'vs-code-aster.restartLSPServer',
  'vs-code-aster.showCatalogInfo',
];

describe('extension activation', () => {
  it('activates (LSP gated off) and registers all contributed commands', async () => {
    const ext = vscode.extensions.getExtension(EXTENSION_ID);
    assert.ok(ext, `extension ${EXTENSION_ID} should be found`);
    await ext!.activate();
    const commands = await vscode.commands.getCommands(true);
    for (const id of CONTRIBUTED_COMMANDS) {
      assert.ok(commands.includes(id), `command should be registered: ${id}`);
    }
  });
});
