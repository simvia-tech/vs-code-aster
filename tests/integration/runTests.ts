import * as path from 'path';
import { runTests } from '@vscode/test-electron';

async function main(): Promise<void> {
  try {
    // Compiled to out-test/integration/runTests.js → repo root is two up.
    const extensionDevelopmentPath = path.resolve(__dirname, '../../');
    const extensionTestsPath = path.resolve(__dirname, './suite/index');

    await runTests({
      extensionDevelopmentPath,
      extensionTestsPath,
      launchArgs: ['--disable-extensions'],
      // Boot fast and deterministically: skip the docker reconcile + LSP launch.
      extensionTestsEnv: { VS_CODE_ASTER_DISABLE_LSP: '1' },
    });
  } catch (err) {
    console.error('Failed to run integration tests:', err);
    process.exit(1);
  }
}

void main();
