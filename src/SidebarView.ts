import * as vscode from 'vscode';
import * as fs from 'fs';
import {
  caveFilePath,
  dockerAvailable,
  getBundledVersion,
  getSelectedCaveVersion,
} from './CatalogResolver';
import { listInstalledVersions } from './CaveStatusBar';
import { probeLspDeps, probeRuff, runProc } from './PythonEnv';

const VIEW_ID = 'vs-code-aster.sidebar';

type Status = 'ok' | 'warn' | 'error' | 'info';

interface Probe {
  pythonOk: boolean;
  pythonMissing: string[];
  ruffOk: boolean;
  dockerOk: boolean;
  caveOk: boolean;
  installedVersions: string[];
  currentVersion: string | null;
  bundledVersion: string | null;
}

class Item extends vscode.TreeItem {
  children?: Item[];
  constructor(
    label: string | vscode.TreeItemLabel,
    collapsible: vscode.TreeItemCollapsibleState = vscode.TreeItemCollapsibleState.None
  ) {
    super(label, collapsible);
  }
}

function statusIcon(s: Status): vscode.ThemeIcon {
  switch (s) {
    case 'ok':
      return new vscode.ThemeIcon('pass-filled', new vscode.ThemeColor('testing.iconPassed'));
    case 'warn':
      return new vscode.ThemeIcon('warning', new vscode.ThemeColor('list.warningForeground'));
    case 'error':
      return new vscode.ThemeIcon('error', new vscode.ThemeColor('list.errorForeground'));
    case 'info':
      return new vscode.ThemeIcon('info');
  }
}

async function caveOnPath(): Promise<boolean> {
  const r = await runProc(process.platform === 'win32' ? 'where' : 'which', ['cave'], 3_000);
  return r.code === 0;
}

export class SidebarProvider implements vscode.TreeDataProvider<Item> {
  private _onDidChangeTreeData = new vscode.EventEmitter<Item | undefined | void>();
  public readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

  private cached: Probe | null = null;
  private probing: Promise<void> | null = null;
  private caveWatcher?: fs.FSWatcher;
  private caveDebounce?: NodeJS.Timeout;

  constructor(private readonly context: vscode.ExtensionContext) {
    // Re-render on relevant config changes.
    context.subscriptions.push(
      vscode.workspace.onDidChangeConfiguration((e) => {
        if (e.affectsConfiguration('vs-code-aster')) {
          this.refresh();
        }
      })
    );
    // Re-render whenever ~/.cave changes (cave use, install, remove).
    try {
      this.caveWatcher = fs.watch(caveFilePath(), () => {
        if (this.caveDebounce) {
          clearTimeout(this.caveDebounce);
        }
        this.caveDebounce = setTimeout(() => this.refresh(), 300);
      });
      context.subscriptions.push({ dispose: () => this.caveWatcher?.close() });
    } catch {
      /* ~/.cave may not exist yet */
    }
  }

  refresh(): void {
    this.cached = null;
    this._onDidChangeTreeData.fire();
  }

  getTreeItem(item: Item): vscode.TreeItem {
    return item;
  }

  async getChildren(parent?: Item): Promise<Item[]> {
    if (!parent) {
      return this.topLevel();
    }
    return parent.children ?? [];
  }

  // -------------------------------------------------------- top-level

  private async topLevel(): Promise<Item[]> {
    const probe = await this.getProbe();
    return [
      this.setupGroup(probe),
      this.actionsGroup(),
      this.versionsGroup(probe),
      this.settingsGroup(),
    ];
  }

  // --------------------------------------------------------------- probes

  private async getProbe(): Promise<Probe> {
    if (this.cached) {
      return this.cached;
    }
    if (!this.probing) {
      this.probing = this.runProbes().finally(() => {
        this.probing = null;
      });
    }
    await this.probing;
    return (
      this.cached ?? {
        pythonOk: false,
        pythonMissing: [],
        ruffOk: false,
        dockerOk: false,
        caveOk: false,
        installedVersions: [],
        currentVersion: null,
        bundledVersion: null,
      }
    );
  }

  private async runProbes(): Promise<void> {
    const [pythonResult, ruffOk, dockerOk, caveOk, installed] = await Promise.all([
      probeLspDeps(this.context),
      probeRuff(this.context),
      dockerAvailable(),
      caveOnPath(),
      listInstalledVersions(),
    ]);
    this.cached = {
      pythonOk: pythonResult.ok,
      pythonMissing: pythonResult.missing,
      ruffOk,
      dockerOk,
      caveOk,
      installedVersions: installed,
      currentVersion: getSelectedCaveVersion(),
      bundledVersion: getBundledVersion(this.context),
    };
  }

  // ------------------------------------------------------------ Setup

  private setupGroup(p: Probe): Item {
    const versionOk = !!p.currentVersion && p.installedVersions.includes(p.currentVersion);
    const allOk = p.pythonOk && p.ruffOk && p.dockerOk && p.caveOk && versionOk;
    const item = new Item(
      'Setup',
      allOk ? vscode.TreeItemCollapsibleState.Collapsed : vscode.TreeItemCollapsibleState.Expanded
    );
    item.iconPath = new vscode.ThemeIcon('checklist');
    const versionStatus: Status = versionOk ? 'ok' : 'warn';

    const items: Item[] = [
      this.statusItem(
        'Python LSP dependencies',
        p.pythonOk ? 'ok' : 'warn',
        p.pythonOk
          ? 'pygls, numpy, medcoupling installed'
          : `missing: ${p.pythonMissing.join(', ') || '?'}`,
        'vs-code-aster.runSetup'
      ),
      this.statusItem(
        'ruff (formatter)',
        p.ruffOk ? 'ok' : 'warn',
        p.ruffOk ? 'available' : 'not installed',
        'vs-code-aster.runSetup'
      ),
      this.statusItem(
        'Docker',
        p.dockerOk ? 'ok' : 'warn',
        p.dockerOk ? 'running' : 'not available',
        'vs-code-aster.runSetup'
      ),
      this.statusItem(
        'cave',
        p.caveOk ? 'ok' : 'warn',
        p.caveOk ? 'on PATH' : 'not installed',
        'vs-code-aster.runSetup'
      ),
      this.statusItem(
        'code_aster version',
        versionStatus,
        p.installedVersions.length === 0
          ? 'no image installed'
          : p.currentVersion && p.installedVersions.includes(p.currentVersion)
            ? `using ${p.currentVersion}`
            : `bundled ${p.bundledVersion ?? '?'} fallback`,
        // No image installed → straight to the install picker; otherwise
        // open the regular picker so the user can switch / install / remove.
        p.installedVersions.length === 0
          ? 'vs-code-aster.installCaveVersion'
          : 'vs-code-aster.selectCaveVersion'
      ),
    ];
    item.children = items;
    return item;
  }

  private statusItem(label: string, status: Status, description: string, command: string): Item {
    const it = new Item(label);
    it.iconPath = statusIcon(status);
    it.description = description;
    it.tooltip = `${label}: ${description}`;
    it.command = { title: 'Run setup checks', command };
    return it;
  }

  // ---------------------------------------------------------- Actions

  private actionsGroup(): Item {
    const item = new Item('Quick actions', vscode.TreeItemCollapsibleState.Expanded);
    item.iconPath = new vscode.ThemeIcon('rocket');
    item.children = [
      this.actionItem('New export file…', 'new-file', 'vs-code-aster.exportDoc'),
      this.actionItem('Run with code_aster', 'play', 'vs-code-aster.run-aster'),
      this.actionItem('Open mesh viewer', 'eye', 'vs-code-aster.meshViewer'),
      this.actionItem('Restart language server', 'sync', 'vs-code-aster.restartLSPServer'),
      this.actionItem('Run setup checks', 'checklist', 'vs-code-aster.runSetup'),
      this.actionItem('Show catalog info', 'info', 'vs-code-aster.showCatalogInfo'),
    ];
    return item;
  }

  private actionItem(label: string, icon: string, command: string): Item {
    const it = new Item(label);
    it.iconPath = new vscode.ThemeIcon(icon);
    it.command = { title: label, command };
    return it;
  }

  // ---------------------------------------------------------- Versions

  private versionsGroup(p: Probe): Item {
    const item = new Item('Versions', vscode.TreeItemCollapsibleState.Expanded);
    item.iconPath = new vscode.ThemeIcon('versions');
    const children: Item[] = [];
    if (!p.caveOk) {
      const missing = new Item('cave is not installed');
      missing.iconPath = statusIcon('warn');
      missing.command = { title: 'Set up', command: 'vs-code-aster.runSetup' };
      missing.description = 'click to run setup';
      children.push(missing);
    } else if (p.installedVersions.length === 0) {
      const empty = new Item('No code_aster image installed');
      empty.iconPath = statusIcon('warn');
      empty.description = 'click to install';
      empty.command = { title: 'Install', command: 'vs-code-aster.installCaveVersion' };
      children.push(empty);
    } else {
      for (const v of p.installedVersions) {
        const it = new Item(v);
        const isCurrent = v === p.currentVersion;
        it.description = isCurrent ? '(current)' : undefined;
        it.iconPath = new vscode.ThemeIcon(
          isCurrent ? 'check' : 'circle-outline',
          isCurrent ? new vscode.ThemeColor('testing.iconPassed') : undefined
        );
        // Click → cave use <v> directly. The wrapper skips no-ops when
        // <v> is already current.
        it.command = {
          title: 'Switch',
          command: 'vs-code-aster.switchCaveVersion',
          arguments: [v],
        };
        children.push(it);
      }
    }
    const install = new Item('Install another version…');
    install.iconPath = new vscode.ThemeIcon('cloud-download');
    install.command = { title: 'Install', command: 'vs-code-aster.installCaveVersion' };
    children.push(install);
    item.children = children;
    return item;
  }

  // ---------------------------------------------------------- Settings

  private settingsGroup(): Item {
    const item = new Item('Settings', vscode.TreeItemCollapsibleState.Collapsed);
    item.iconPath = new vscode.ThemeIcon('settings-gear');
    item.children = [
      this.settingItem('Python interpreter', 'vs-code-aster.pythonExecutablePath', 'terminal'),
      this.settingItem('Formatter', 'vs-code-aster.formatter', 'wand'),
      this.settingItem('Run alias', 'vs-code-aster.aliasForRun', 'play-circle'),
      this.settingItem('Catalog path (override)', 'vs-code-aster.asterCatalogPath', 'library'),
      this.settingItem(
        'Supported .comm extensions',
        'vs-code-aster.commFileExtensions',
        'file-code'
      ),
      this.settingItem(
        'Supported MED extensions',
        'vs-code-aster.medFileExtensions',
        'file-binary'
      ),
      this.settingItem('Max run logs', 'vs-code-aster.maxRunLogs', 'history'),
    ];
    return item;
  }

  private settingItem(label: string, key: string, icon: string): Item {
    const it = new Item(label);
    it.iconPath = new vscode.ThemeIcon(icon);
    const config = vscode.workspace.getConfiguration();
    const value = config.get<unknown>(key);
    it.description = formatSettingValue(value);
    it.tooltip = `${key} = ${JSON.stringify(value)}`;
    it.command = {
      title: 'Open setting',
      command: 'workbench.action.openSettings',
      arguments: [key],
    };
    return it;
  }
}

function formatSettingValue(v: unknown): string {
  if (v === undefined || v === null || v === '') {
    return '(default)';
  }
  if (Array.isArray(v)) {
    return v.length > 4 ? `${v.slice(0, 4).join(', ')}, +${v.length - 4}` : v.join(', ');
  }
  if (typeof v === 'string') {
    return v.length > 40 ? v.slice(0, 37) + '…' : v;
  }
  return String(v);
}

export function registerSidebar(context: vscode.ExtensionContext): SidebarProvider {
  const provider = new SidebarProvider(context);
  context.subscriptions.push(
    vscode.window.registerTreeDataProvider(VIEW_ID, provider),
    vscode.commands.registerCommand('vs-code-aster.sidebar.refresh', () => provider.refresh())
  );
  return provider;
}
