import * as vscode from 'vscode';
import * as fs from 'fs';
import { spawn } from 'child_process';
import {
  caveFilePath,
  clearCatalogCacheFor,
  getBundledVersion,
  getSelectedCaveVersion,
  reconcileCatalogCache,
} from './CatalogResolver';
import { LspServer } from './LspServer';

const COMMAND_ID = 'vs-code-aster.selectCaveVersion';

function exec(
  cmd: string,
  args: string[],
  timeoutMs = 5_000
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

// List installed versions by querying docker directly (~20ms) instead of
// `cave list` (~100ms + update-check latency on cold runs). `cave` itself
// is just a wrapper over `docker images` for listing.
// Compare version tags like "17.4.0" / "16.9.0" — split on non-digits and
// compare segment-wise numerically. Returns >0 if b > a (so Array.sort puts
// the newest first).
function compareVersionsDesc(a: string, b: string): number {
  const pa = a
    .split(/[^0-9]+/)
    .filter(Boolean)
    .map(Number);
  const pb = b
    .split(/[^0-9]+/)
    .filter(Boolean)
    .map(Number);
  const n = Math.max(pa.length, pb.length);
  for (let i = 0; i < n; i++) {
    const ai = pa[i] ?? 0;
    const bi = pb[i] ?? 0;
    if (ai !== bi) {
      return bi - ai;
    }
  }
  return b.localeCompare(a);
}

async function listInstalledVersions(): Promise<string[]> {
  const r = await exec('docker', ['images', '--format', '{{.Tag}}', 'simvia/code_aster']);
  if (r.code !== 0) {
    return [];
  }
  return Array.from(
    new Set(
      r.stdout
        .split(/\r?\n/)
        .map((s) => s.trim())
        .filter((s) => s && s !== '<none>')
    )
  ).sort(compareVersionsDesc);
}

interface AvailableVersion {
  tag: string;
  date: string;
}

async function listAvailableVersions(): Promise<AvailableVersion[]> {
  const r = await exec('cave', ['available'], 15_000);
  if (r.code !== 0) {
    return [];
  }
  const out: AvailableVersion[] = [];
  for (const line of r.stdout.split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed || /^Tag\s+Date/i.test(trimmed)) {
      continue;
    }
    const m = trimmed.match(/^(\S+)\s+(.*)$/);
    if (m) {
      out.push({ tag: m[1], date: m[2].trim() });
    }
  }
  return out.sort((a, b) => compareVersionsDesc(a.tag, b.tag));
}

export class CaveStatusBar {
  private static _instance: CaveStatusBar | null = null;
  private item: vscode.StatusBarItem;
  private disposables: vscode.Disposable[] = [];
  private caveWatcher?: fs.FSWatcher;
  private caveDebounce?: NodeJS.Timeout;
  private cachedVersions: string[] = [];
  private versionsRefreshing: Promise<void> | null = null;
  private context?: vscode.ExtensionContext;

  private constructor() {
    this.item = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 50);
    this.item.command = COMMAND_ID;
  }

  public static get instance(): CaveStatusBar {
    if (!CaveStatusBar._instance) {
      CaveStatusBar._instance = new CaveStatusBar();
    }
    return CaveStatusBar._instance;
  }

  public activate(context: vscode.ExtensionContext) {
    this.context = context;
    context.subscriptions.push(
      vscode.commands.registerCommand(COMMAND_ID, () => this.pickVersion())
    );

    this.disposables.push(
      vscode.window.onDidChangeActiveTextEditor((editor) => this.refresh(editor))
    );
    this.watchCave();

    this.refresh(vscode.window.activeTextEditor);
    // Pre-warm the cache so the first click is instant; also re-refresh the
    // status bar label once we know the true set of installed versions, so
    // a stale ~/.cave doesn't linger as the displayed version.
    void this.refreshVersions().then(() => this.refresh(vscode.window.activeTextEditor));

    context.subscriptions.push(this.item, ...this.disposables);
  }

  private refreshVersions(): Promise<void> {
    if (this.versionsRefreshing) {
      return this.versionsRefreshing;
    }
    this.versionsRefreshing = listInstalledVersions()
      .then((v) => {
        this.cachedVersions = v;
      })
      .finally(() => {
        this.versionsRefreshing = null;
      });
    return this.versionsRefreshing;
  }

  private static readonly ASTER_LANGS = new Set(['comm', 'export']);

  private refresh(editor: vscode.TextEditor | undefined) {
    if (!editor || !CaveStatusBar.ASTER_LANGS.has(editor.document.languageId)) {
      this.item.hide();
      return;
    }
    // Re-query docker in the background so externally-removed images (e.g.
    // `docker rmi simvia/code_aster:17.4.0` run from a terminal) are
    // reflected in the label. `refreshVersions` is dedup'd internally, so
    // rapid editor changes won't cause a storm.
    void this.refreshVersions().then(() => this.renderLabel());
    this.renderLabel();
  }

  private renderLabel() {
    const selected = getSelectedCaveVersion();
    // `~/.cave` can point at a version whose image has since been removed
    // (either by us via the trash button, or manually via `docker rmi`).
    // Only use it when the image actually exists on this host.
    const isInstalled = selected !== null && this.cachedVersions.includes(selected);
    if (selected && isInstalled) {
      this.item.text = selected;
      this.item.tooltip = new vscode.MarkdownString(
        `Using **code_aster ${selected}** via cave.\n\n` +
          `Click to switch version, install a new one, or remove this one.`
      );
      this.item.backgroundColor = undefined;
    } else {
      const bundled = this.context ? getBundledVersion(this.context) : null;
      const label = bundled ? `${bundled} (bundled)` : 'bundled';
      this.item.text = `$(warning) ${label}`;
      this.item.tooltip = new vscode.MarkdownString(
        `**No cave-installed code_aster version selected.**\n\n` +
          `Language features (completion, hover, signatures) are served from ` +
          `the **bundled ${bundled ?? '?'} catalog**, which is enough for ` +
          `editing but **\`cave run\` will not work** until you install and ` +
          `select a version.\n\n` +
          `Click to install or select a version.`
      );
      this.item.backgroundColor = new vscode.ThemeColor('statusBarItem.warningBackground');
    }
    this.item.show();
  }

  private watchCave() {
    try {
      this.caveWatcher = fs.watch(caveFilePath(), () => {
        if (this.caveDebounce) {
          clearTimeout(this.caveDebounce);
        }
        this.caveDebounce = setTimeout(() => this.refresh(vscode.window.activeTextEditor), 300);
      });
    } catch {
      /* ~/.cave not present yet */
    }
  }

  private static readonly REMOVE_BUTTON: vscode.QuickInputButton = {
    iconPath: new vscode.ThemeIcon('trash'),
    tooltip: 'Remove this version (docker rmi)',
  };

  // Identity-based sentinel so we can tell the "install" row apart from real
  // version rows without relying on label string comparison (codicon prefixes
  // can trip that up).
  private installItem: (vscode.QuickPickItem & { isInstall: true }) | null = null;

  private buildItems(versions: string[], current: string | null): vscode.QuickPickItem[] {
    this.installItem = {
      label: '$(cloud-download)  Install a new version…',
      detail: versions.length === 0 ? 'No versions installed yet.' : undefined,
      alwaysShow: true,
      isInstall: true,
    };
    if (versions.length === 0) {
      return [this.installItem];
    }
    const separator: vscode.QuickPickItem = {
      label: 'Installed',
      kind: vscode.QuickPickItemKind.Separator,
    };
    const items: vscode.QuickPickItem[] = versions.map((v) => ({
      label: v,
      description: v === current ? '(current)' : undefined,
      picked: v === current,
      buttons: [CaveStatusBar.REMOVE_BUTTON],
    }));
    return [this.installItem, separator, ...items];
  }

  private async pickVersion() {
    const current = getSelectedCaveVersion();
    const qp = vscode.window.createQuickPick();
    qp.placeholder = 'Select code_aster version';
    qp.matchOnDescription = true;
    qp.items = this.buildItems(this.cachedVersions, current);
    qp.busy = this.cachedVersions.length === 0;
    qp.show();

    void this.refreshVersions().then(() => {
      qp.items = this.buildItems(this.cachedVersions, current);
      qp.busy = false;
    });

    const action = await new Promise<
      { kind: 'pick'; item: vscode.QuickPickItem } | { kind: 'remove'; tag: string } | undefined
    >((resolve) => {
      qp.onDidAccept(() =>
        resolve({ kind: 'pick', item: qp.selectedItems[0] ?? qp.activeItems[0] })
      );
      qp.onDidTriggerItemButton((e) => {
        if (e.button === CaveStatusBar.REMOVE_BUTTON) {
          resolve({ kind: 'remove', tag: e.item.label });
        }
      });
      qp.onDidHide(() => resolve(undefined));
    });
    qp.dispose();

    if (!action) {
      return;
    }
    if (action.kind === 'remove') {
      await this.removeVersion(action.tag, current);
      return;
    }
    const picked = action.item;
    if (!picked) {
      return;
    }
    if ((picked as { isInstall?: boolean }).isInstall) {
      await this.installNewVersion(current);
      return;
    }
    if (picked.label === current) {
      return;
    }

    const r = await exec('cave', ['use', picked.label], 10_000);
    if (r.code !== 0) {
      vscode.window.showErrorMessage(
        `cave use ${picked.label} failed: ${r.stderr.trim() || r.stdout.trim()}`
      );
      return;
    }
    this.refresh(vscode.window.activeTextEditor);
    void LspServer.instance.restart();
    vscode.window.showInformationMessage(`code_aster version set to ${picked.label}.`);
  }

  private async removeVersion(tag: string, current: string | null) {
    const warnCurrent = tag === current ? '\n\nThis is the currently selected version.' : '';
    const savedTooltip = this.item.tooltip;
    // Mouse is still over the status-bar item after the click — clear the
    // tooltip so it doesn't cover the confirmation modal / info toast.
    this.item.tooltip = undefined;
    const ok = await vscode.window.showWarningMessage(
      `Remove code_aster ${tag}? This runs \`docker rmi simvia/code_aster:${tag}\` and cannot be undone.${warnCurrent}`,
      { modal: true },
      'Remove'
    );
    if (ok !== 'Remove') {
      this.item.tooltip = savedTooltip;
      return;
    }
    const r = await exec('docker', ['rmi', `simvia/code_aster:${tag}`], 30_000);
    if (r.code !== 0) {
      vscode.window.showErrorMessage(
        `docker rmi simvia/code_aster:${tag} failed: ${r.stderr.trim() || r.stdout.trim()}`
      );
      this.item.tooltip = savedTooltip;
      return;
    }
    clearCatalogCacheFor(tag);
    vscode.window.showInformationMessage(`code_aster ${tag} removed.`);
    this.cachedVersions = this.cachedVersions.filter((v) => v !== tag);
    this.refresh(vscode.window.activeTextEditor);
    void this.refreshVersions().then(() => {
      this.refresh(vscode.window.activeTextEditor);
      // If we just removed the version the LSP is currently backed by, the
      // running server is still serving a catalog from a now-deleted cache
      // dir. Restart so it re-resolves (will fall back to bundled or to
      // whatever ~/.cave now points at).
      if (tag === current) {
        void LspServer.instance.restart();
      }
    });
  }

  private async installNewVersion(rawCurrent: string | null) {
    // Treat a selection pointing at a missing image as "nothing selected" so
    // the user can re-install that exact version without hitting the
    // already-current short-circuit below.
    const current = rawCurrent && this.cachedVersions.includes(rawCurrent) ? rawCurrent : null;
    const qp = vscode.window.createQuickPick();
    qp.placeholder = 'Install a code_aster version (fetching from DockerHub…)';
    qp.matchOnDescription = true;
    qp.busy = true;
    qp.show();

    const [available] = await Promise.all([listAvailableVersions()]);
    const installed = new Set(this.cachedVersions);
    // Split into two groups: already-installed (shown first, as a no-op
    // in practice — picking just switches to that version) and available
    // for download. Grouping with separators avoids per-item markers that
    // only show on hover.
    const installedItems: vscode.QuickPickItem[] = [];
    const availableItems: vscode.QuickPickItem[] = [];
    for (const v of available) {
      const item: vscode.QuickPickItem = { label: v.tag, description: v.date };
      if (installed.has(v.tag)) {
        installedItems.push(item);
      } else {
        availableItems.push(item);
      }
    }
    const grouped: vscode.QuickPickItem[] = [];
    if (installedItems.length) {
      grouped.push({ label: 'Installed', kind: vscode.QuickPickItemKind.Separator });
      grouped.push(...installedItems);
    }
    if (availableItems.length) {
      grouped.push({ label: 'Available', kind: vscode.QuickPickItemKind.Separator });
      grouped.push(...availableItems);
    }
    qp.items = grouped;
    qp.busy = false;

    if (grouped.length === 0) {
      qp.hide();
      qp.dispose();
      vscode.window.showWarningMessage(
        '`cave available` returned no versions. Check your network or that cave is on PATH.'
      );
      return;
    }

    const picked = await new Promise<vscode.QuickPickItem | undefined>((resolve) => {
      qp.onDidAccept(() => resolve(qp.selectedItems[0]));
      qp.onDidHide(() => resolve(undefined));
    });
    qp.dispose();
    if (!picked || picked.label === current) {
      return;
    }
    if (installed.has(picked.label)) {
      // Already installed — no need to re-pull, just switch.
      const r = await exec('cave', ['use', picked.label], 10_000);
      if (r.code !== 0) {
        vscode.window.showErrorMessage(
          `cave use ${picked.label} failed: ${r.stderr.trim() || r.stdout.trim()}`
        );
        return;
      }
      void LspServer.instance.restart();
      return;
    }

    await this.installVersionWithProgress(picked.label);
  }

  private installVersionWithProgress(version: string): Thenable<void> {
    // VS Code shows the status-bar tooltip whenever the mouse is over the
    // item — which is exactly where the user's cursor is right after they
    // clicked it. That tooltip would then cover the install progress
    // notification. Clear it for the duration of the install; the refresh()
    // call at the end restores it from the real state.
    const savedTooltip = this.item.tooltip;
    this.item.tooltip = undefined;
    return vscode.window.withProgress(
      {
        location: vscode.ProgressLocation.Notification,
        title: `Installing code_aster ${version}`,
        cancellable: true,
      },
      (progress, token) =>
        new Promise<void>((resolve) => {
          const child = spawn('cave', ['use', version], { stdio: ['pipe', 'pipe', 'pipe'] });
          // Auto-confirm the "Download it? (y/n)" prompt.
          child.stdin.write('y\n');
          child.stdin.end();

          let currentPhase = 'Starting…';
          progress.report({ message: currentPhase });

          const classifyPhase = (line: string): string | null => {
            // Map raw docker / cave output to a short, stable phase label so
            // the notification doesn't flicker through every progress line.
            if (/Downloading/i.test(line)) {
              return 'Downloading image…';
            }
            if (/Extracting|Verifying Checksum/i.test(line)) {
              return 'Extracting…';
            }
            if (/Pull complete|Digest:|Status: (Downloaded|Image is up to date)/i.test(line)) {
              return 'Finalizing…';
            }
            if (/Pulling (from|fs layer)/i.test(line)) {
              return 'Pulling image…';
            }
            return null;
          };

          const handleStream = (chunk: Buffer) => {
            const text = chunk.toString();
            const fragments = text
              .split(/[\r\n]+/)
              .map((s) => s.trim())
              .filter(Boolean);
            for (const line of fragments) {
              const phase = classifyPhase(line);
              if (phase && phase !== currentPhase) {
                currentPhase = phase;
                progress.report({ message: currentPhase });
              }
            }
          };
          child.stdout.on('data', handleStream);
          child.stderr.on('data', handleStream);

          token.onCancellationRequested(() => {
            child.kill('SIGTERM');
          });

          child.on('error', (err) => {
            vscode.window.showErrorMessage(`cave install failed: ${err.message}`);
            resolve();
          });
          child.on('close', (code) => {
            if (token.isCancellationRequested) {
              vscode.window.showWarningMessage(
                `Installation of code_aster ${version} was cancelled.`
              );
            } else if (code !== 0) {
              vscode.window.showErrorMessage(
                `cave use ${version} exited with code ${code} during "${currentPhase}".`
              );
            } else {
              vscode.window.showInformationMessage(`code_aster ${version} installed.`);
              // Invalidate cached versions so the next picker shows it as installed.
              void this.refreshVersions();
              // Our ~/.cave watcher already triggers an LSP restart.
            }
            resolve();
          });
        }).finally(() => {
          // Restore tooltip. A full refresh() rebuilds it from current state
          // (may have changed if the selected version is now installed).
          this.item.tooltip = savedTooltip;
          this.refresh(vscode.window.activeTextEditor);
        })
    );
  }

  public dispose() {
    this.item.dispose();
    this.disposables.forEach((d) => d.dispose());
    this.caveWatcher?.close();
  }
}
