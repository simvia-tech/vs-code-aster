import * as vscode from 'vscode';
import { spawn } from 'child_process';
import { resolvePythonExecutable } from './PythonEnv';

const CHANNEL_NAME = 'code_aster: Formatter';
let channel: vscode.OutputChannel | undefined;
let missingToolWarned = false;

function log(line: string) {
  if (!channel) {
    channel = vscode.window.createOutputChannel(CHANNEL_NAME);
  }
  const stamp = new Date().toISOString().slice(11, 23);
  channel.appendLine(`${stamp} ${line}`);
}

/**
 * Resolve the command and args used to format a `.comm` file. Default is
 * the configured Python interpreter running `ruff format`. Users can override
 * `vs-code-aster.formatter` with a full shell command if they prefer a
 * different tool (black, a wrapper script, …).
 */
function resolveFormatterCommand(
  context: vscode.ExtensionContext,
  documentPath: string
): { cmd: string; args: string[] } | null {
  const config = vscode.workspace.getConfiguration('vs-code-aster');
  const formatter = (config.get<string>('formatter') || 'ruff').trim();
  if (!formatter || formatter === 'off') {
    return null;
  }

  if (formatter !== 'ruff') {
    const parts = formatter.split(/\s+/).filter(Boolean);
    if (parts.length === 0) {
      return null;
    }
    return { cmd: parts[0], args: parts.slice(1) };
  }

  const python = resolvePythonExecutable(context);
  return {
    cmd: python,
    args: [
      '-m',
      'ruff',
      'format',
      '--config',
      'format.quote-style="preserve"',
      '--line-length=100',
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
  constructor(private context: vscode.ExtensionContext) {}

  async provideDocumentFormattingEdits(
    document: vscode.TextDocument
  ): Promise<vscode.TextEdit[] | undefined> {
    return this.format(document);
  }

  async provideDocumentRangeFormattingEdits(
    document: vscode.TextDocument,
    range: vscode.Range
  ): Promise<vscode.TextEdit[] | undefined> {
    const text = document.getText(range);
    const edits = await this.formatText(document, text);
    if (!edits) {
      return undefined;
    }
    return [vscode.TextEdit.replace(range, edits[0].newText)];
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
    const resolved = resolveFormatterCommand(this.context, document.uri.fsPath);
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
            'ruff is not available for formatting. Run "code_aster: Run setup checks" to install it.',
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
