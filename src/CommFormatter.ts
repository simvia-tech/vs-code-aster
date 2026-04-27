import * as vscode from 'vscode';
import { spawn } from 'child_process';

const CHANNEL_NAME = 'code_aster: Formatter';
let channel: vscode.OutputChannel | undefined;
let missingToolWarned = false;
let ruffPromptShown = false;
let ruffProbeResult: boolean | null = null;

function log(line: string) {
  if (!channel) {
    channel = vscode.window.createOutputChannel(CHANNEL_NAME);
  }
  const stamp = new Date().toISOString().slice(11, 23);
  channel.appendLine(`${stamp} ${line}`);
}

function pythonExecutable(): string {
  return (
    vscode.workspace.getConfiguration('vs-code-aster').get<string>('pythonExecutablePath') ||
    'python3'
  );
}

function runOnce(
  cmd: string,
  args: string[],
  timeoutMs = 10_000
): Promise<{ code: number; stdout: string; stderr: string }> {
  return new Promise((resolve) => {
    const child = spawn(cmd, args, { stdio: ['ignore', 'pipe', 'pipe'] });
    let stdout = '';
    let stderr = '';
    const timer = setTimeout(() => child.kill('SIGKILL'), timeoutMs);
    child.stdout.on('data', (d) => (stdout += d.toString()));
    child.stderr.on('data', (d) => (stderr += d.toString()));
    child.on('error', (err) => {
      clearTimeout(timer);
      resolve({ code: -1, stdout, stderr: stderr + String(err) });
    });
    child.on('close', (code) => {
      clearTimeout(timer);
      resolve({ code: code ?? -1, stdout, stderr });
    });
  });
}

async function ruffIsInstalled(): Promise<boolean> {
  if (ruffProbeResult !== null) {
    return ruffProbeResult;
  }
  const r = await runOnce(pythonExecutable(), ['-m', 'ruff', '--version'], 5_000);
  ruffProbeResult = r.code === 0;
  log(`ruff probe: ${ruffProbeResult ? 'present' : `missing (${r.stderr.trim().slice(0, 120)})`}`);
  return ruffProbeResult;
}

/**
 * If the formatter is set to `ruff` and ruff isn't installed in the
 * configured Python, offer to install it. Called when the first `.comm`
 * file is opened. Dedup'd to run at most once per session.
 */
export async function offerInstallRuff(context: vscode.ExtensionContext) {
  if (ruffPromptShown) {
    return;
  }
  const config = vscode.workspace.getConfiguration('vs-code-aster');
  const formatter = (config.get<string>('formatter') || 'ruff').trim();
  if (formatter !== 'ruff') {
    return;
  }
  // Respect "don't ask again" stored decision.
  if (context.globalState.get<boolean>('formatter.ruffDeclined')) {
    return;
  }
  if (await ruffIsInstalled()) {
    return;
  }
  ruffPromptShown = true;

  const choice = await vscode.window.showInformationMessage(
    'Install `ruff` to enable code_aster file formatting? It will be installed into the Python used by the extension (' +
      pythonExecutable() +
      ').',
    'Install',
    'Not now',
    "Don't ask again"
  );

  if (choice === "Don't ask again") {
    await context.globalState.update('formatter.ruffDeclined', true);
    return;
  }
  if (choice !== 'Install') {
    return;
  }
  await installRuff();
}

async function installRuff(): Promise<void> {
  const python = pythonExecutable();
  await vscode.window.withProgress(
    {
      location: vscode.ProgressLocation.Notification,
      title: 'Installing ruff…',
      cancellable: false,
    },
    async (progress) => {
      // Let pip decide where to install: inside a venv it goes into the venv;
      // a system Python will fall back to site-packages (and on PEP 668
      // systems we catch the failure below). Passing `--user` unconditionally
      // breaks venvs ("User site-packages are not visible in this virtualenv").
      progress.report({ message: `${python} -m pip install ruff` });
      log(`$ ${python} -m pip install ruff`);
      let r = await runOnce(python, ['-m', 'pip', 'install', 'ruff'], 120_000);
      // PEP 668 / "externally-managed-environment" → retry with --user which
      // is the documented escape hatch for that case.
      if (r.code !== 0 && /externally[- ]managed/i.test(r.stderr)) {
        log('retrying with --user (externally-managed environment)');
        r = await runOnce(python, ['-m', 'pip', 'install', '--user', 'ruff'], 120_000);
      }
      if (r.code !== 0) {
        log(`pip install failed (${r.code}): ${r.stderr.trim().slice(0, 500)}`);
        const choice = await vscode.window.showErrorMessage(
          `Could not install ruff: ${r.stderr.trim().split('\n').slice(-1)[0] || 'exit ' + r.code}`,
          'Show log'
        );
        if (choice === 'Show log' && channel) {
          channel.show();
        }
        return;
      }
      log('ruff installed successfully');
      ruffProbeResult = true; // optimistic; next format will validate
      vscode.window.showInformationMessage('ruff installed. Formatting is ready.');
    }
  );
}

/**
 * Resolve the command and args used to format a `.comm` file. Default is
 * the configured Python interpreter running `ruff format`. Users can override
 * `vs-code-aster.formatter` with a full shell command if they prefer a
 * different tool (black, a wrapper script, …).
 */
function resolveFormatterCommand(documentPath: string): { cmd: string; args: string[] } | null {
  const config = vscode.workspace.getConfiguration('vs-code-aster');
  const formatter = (config.get<string>('formatter') || 'ruff').trim();
  if (!formatter || formatter === 'off') {
    return null;
  }

  // A user-supplied shell command: split on whitespace (naïve but matches
  // the setting contract — one string, no fancy quoting expected).
  if (formatter !== 'ruff') {
    const parts = formatter.split(/\s+/).filter(Boolean);
    if (parts.length === 0) {
      return null;
    }
    return { cmd: parts[0], args: parts.slice(1) };
  }

  const python = config.get<string>('pythonExecutablePath') || 'python3';
  return {
    cmd: python,
    args: [
      '-m',
      'ruff',
      'format',
      // Preserve user-chosen quote style; without this ruff flips 'MED' to "MED".
      '--config',
      'format.quote-style="preserve"',
      '--line-length=100',
      // Force .comm to be treated as Python source.
      '--extension',
      'comm:python',
      '--stdin-filename',
      documentPath,
      '-',
    ],
  };
}

function formatStdin(
  cmd: string,
  args: string[],
  stdin: string,
  timeoutMs = 15_000
): Promise<{ code: number; stdout: string; stderr: string }> {
  return new Promise((resolve) => {
    const child = spawn(cmd, args, { stdio: ['pipe', 'pipe', 'pipe'] });
    let stdout = '';
    let stderr = '';
    const timer = setTimeout(() => child.kill('SIGKILL'), timeoutMs);
    child.stdout.on('data', (d) => (stdout += d.toString()));
    child.stderr.on('data', (d) => (stderr += d.toString()));
    child.on('error', (err) => {
      clearTimeout(timer);
      resolve({ code: -1, stdout, stderr: stderr + String(err) });
    });
    child.on('close', (code) => {
      clearTimeout(timer);
      resolve({ code: code ?? -1, stdout, stderr });
    });
    child.stdin.end(stdin);
  });
}

export class CommFormatter
  implements vscode.DocumentFormattingEditProvider, vscode.DocumentRangeFormattingEditProvider
{
  async provideDocumentFormattingEdits(
    document: vscode.TextDocument
  ): Promise<vscode.TextEdit[] | undefined> {
    return this.format(document);
  }

  async provideDocumentRangeFormattingEdits(
    document: vscode.TextDocument,
    range: vscode.Range
  ): Promise<vscode.TextEdit[] | undefined> {
    // ruff format doesn't have a clean range mode; format the selection in
    // isolation. This is best-effort: a selection that spans partial
    // expressions will fail to parse and we'll surface the error.
    const text = document.getText(range);
    const edits = await this.formatText(document, text);
    if (!edits) {
      return undefined;
    }
    // edits is synthesized against a [0,0 .. end] range — rebase onto `range`.
    const formatted = edits[0].newText;
    return [vscode.TextEdit.replace(range, formatted)];
  }

  private async format(document: vscode.TextDocument): Promise<vscode.TextEdit[] | undefined> {
    const text = document.getText();
    const edits = await this.formatText(document, text);
    if (!edits) {
      return undefined;
    }
    const fullRange = new vscode.Range(
      document.positionAt(0),
      document.positionAt(document.getText().length)
    );
    return [vscode.TextEdit.replace(fullRange, edits[0].newText)];
  }

  private async formatText(
    document: vscode.TextDocument,
    text: string
  ): Promise<vscode.TextEdit[] | undefined> {
    const resolved = resolveFormatterCommand(document.uri.fsPath);
    if (!resolved) {
      return undefined;
    }

    log(`$ ${resolved.cmd} ${resolved.args.join(' ')}`);
    const r = await formatStdin(resolved.cmd, resolved.args, text);
    if (r.code === 0) {
      return [vscode.TextEdit.replace(new vscode.Range(0, 0, 0, 0), r.stdout)];
    }

    const stderr = r.stderr.trim();
    log(`formatter exited ${r.code}: ${stderr.slice(0, 1000)}`);

    // Detect "module not found" / "command not found" and surface a single
    // actionable toast instead of a cryptic spawn error.
    const isMissing =
      r.code === -1 ||
      /No module named ruff/i.test(stderr) ||
      /command not found/i.test(stderr) ||
      /ENOENT/i.test(stderr);
    if (isMissing) {
      if (!missingToolWarned) {
        missingToolWarned = true;
        void vscode.window
          .showWarningMessage(
            'ruff is not available for formatting. Install it in the Python interpreter used by the extension (e.g. `pip install ruff`), or set `vs-code-aster.formatter` to your preferred tool.',
            'Show log'
          )
          .then((choice) => {
            if (choice === 'Show log' && channel) {
              channel.show();
            }
          });
      }
      return undefined;
    }

    // Real formatter error (syntax error in the doc, ruff crash, …) —
    // surface it once per invocation so the user can fix.
    void vscode.window
      .showErrorMessage(
        `Formatter failed: ${stderr.split('\n')[0] || `exit ${r.code}`}`,
        'Show log'
      )
      .then((choice) => {
        if (choice === 'Show log' && channel) {
          channel.show();
        }
      });
    return undefined;
  }
}
