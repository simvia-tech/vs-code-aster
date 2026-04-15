/**
 * Keeps `files.associations` in sync with the `vs-code-aster.medFileExtensions` setting.
 *
 * VS Code's `contributes.languages[].extensions` is static (read once from package.json at
 * load time). To let users dynamically map arbitrary extensions (e.g. `.71`, `.72`) to the
 * `med` language — which gives them the MED icon and language ID — we programmatically
 * write `files.associations` entries on activation and whenever the setting changes.
 *
 * Ownership tracking: we only ever touch `files.associations` entries whose value is `med`.
 * Other entries (added by the user or other extensions) are left untouched.
 */
import * as vscode from 'vscode';

const MED_LANGUAGE_ID = 'med';
const SETTING_KEY = 'medFileExtensions';

function normalizeExtension(ext: string): string | null {
  const trimmed = ext.trim();
  if (!trimmed) {
    return null;
  }
  const withDot = trimmed.startsWith('.') ? trimmed : `.${trimmed}`;
  return withDot.toLowerCase();
}

async function syncAssociations(): Promise<void> {
  const asterConfig = vscode.workspace.getConfiguration('vs-code-aster');
  const raw = asterConfig.get<string[]>(SETTING_KEY, ['.med', '.mmed', '.rmed']);

  const desiredPatterns = new Set(
    raw
      .map(normalizeExtension)
      .filter((e): e is string => e !== null)
      .map((ext) => `*${ext}`)
  );

  const filesConfig = vscode.workspace.getConfiguration('files');
  const current = filesConfig.get<Record<string, string>>('associations') ?? {};
  const next: Record<string, string> = {};

  for (const [pattern, language] of Object.entries(current)) {
    if (language === MED_LANGUAGE_ID) {
      continue;
    }
    next[pattern] = language;
  }

  for (const pattern of desiredPatterns) {
    next[pattern] = MED_LANGUAGE_ID;
  }

  const before = JSON.stringify(current);
  const after = JSON.stringify(next);
  if (before === after) {
    return;
  }

  await filesConfig.update('associations', next, vscode.ConfigurationTarget.Global);
}

export function activateMedLanguageSync(context: vscode.ExtensionContext): void {
  void syncAssociations();

  const listener = vscode.workspace.onDidChangeConfiguration((event) => {
    if (event.affectsConfiguration(`vs-code-aster.${SETTING_KEY}`)) {
      void syncAssociations();
    }
  });

  context.subscriptions.push(listener);
}
