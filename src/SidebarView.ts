import * as vscode from 'vscode';
import * as fs from 'fs';
import {
  caveFilePath,
  dockerAvailable,
  getBundledVersion,
  getSelectedCaveVersion,
} from './CatalogResolver';
import { listInstalledVersions } from './CaveStatusBar';
import { LspServer } from './LspServer';
import { probeLspDeps, probeRuff, runProc } from './PythonEnv';

const VIEW_ID = 'vs-code-aster.sidebar';

type Status = 'ok' | 'warn' | 'error' | 'info';

type FamilyKey = 'mesh' | 'material' | 'bcAndLoads' | 'analysis' | 'output';
const FAMILIES: { key: FamilyKey; label: string }[] = [
  { key: 'mesh', label: 'Mesh' },
  { key: 'material', label: 'Material' },
  { key: 'bcAndLoads', label: 'Boundary Conditions & Loads' },
  { key: 'analysis', label: 'Analysis' },
  { key: 'output', label: 'Output' },
];
type CommandFamilies = Record<FamilyKey, string[]>;
const EMPTY_FAMILIES: CommandFamilies = {
  mesh: [],
  material: [],
  bcAndLoads: [],
  analysis: [],
  output: [],
};

interface Probe {
  pythonOk: boolean;
  pythonMissing: string[];
  ruffOk: boolean;
  dockerOk: boolean;
  caveOk: boolean;
  installedVersions: string[];
  currentVersion: string | null;
  bundledVersion: string | null;
  // Command browser data
  inFile: CommandFamilies;
  catalog: CommandFamilies;
  catalogLoaded: boolean;
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

  private _editDebounce?: NodeJS.Timeout;
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
    // The first probe runs at extension activation time, before the LSP
    // has finished starting — so the catalog comes back empty. Refresh
    // when the LSP signals it's ready.
    context.subscriptions.push(
      LspServer.instance.onReady(() => {
        this._catalogCache = null; // re-fetch catalog from the new server.
        this.refresh();
      })
    );
    // Re-render on any active-editor change so the Command browser
    // appears when switching TO a .comm file and disappears when
    // switching AWAY (to .export, plain text, no editor at all, …).
    context.subscriptions.push(
      vscode.window.onDidChangeActiveTextEditor(() => {
        this.refresh();
      }),
      vscode.workspace.onDidChangeTextDocument((event) => {
        if (event.document.languageId !== 'comm') {
          return;
        }
        if (event.document !== vscode.window.activeTextEditor?.document) {
          return;
        }
        if (this._editDebounce) {
          clearTimeout(this._editDebounce);
        }
        this._editDebounce = setTimeout(() => this.refresh(), 300);
      })
    );
  }

  refresh(): void {
    this.cached = null;
    this._onDidChangeTreeData.fire();
  }

  /** Used by the Command browser fuzzy-search QuickPick. Forces a probe
   * if the catalog hasn't been loaded yet. */
  async flatCatalog(): Promise<{ name: string; familyKey: FamilyKey; familyLabel: string }[]> {
    const probe = await this.getProbe();
    const out: { name: string; familyKey: FamilyKey; familyLabel: string }[] = [];
    for (const f of FAMILIES) {
      for (const name of probe.catalog[f.key] ?? []) {
        out.push({ name, familyKey: f.key, familyLabel: f.label });
      }
    }
    out.sort((a, b) => a.name.localeCompare(b.name));
    return out;
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

  /** Required by `TreeView.reveal()`. We only ever reveal top-level
   * group items (which have no parent), so always returning undefined
   * is correct for our usage. */
  getParent(_item: Item): Item | undefined {
    return undefined;
  }

  /** Hold the TreeView so external commands can call reveal(). Set by
   * `registerSidebar` after construction. */
  treeView?: vscode.TreeView<Item>;

  /** Open the panel and expand the Command browser group. Used by the
   * status-bar nudge. */
  async revealCommandBrowser(): Promise<void> {
    // Make sure the activity-bar container is visible first.
    try {
      await vscode.commands.executeCommand('workbench.view.extension.vs-code-aster');
    } catch {
      /* ignore */
    }
    // Force a re-render so we have a fresh Item handle to reveal.
    await this.getProbe();
    const item = this._commandBrowserItem;
    if (item && this.treeView) {
      try {
        await this.treeView.reveal(item, { expand: true, focus: true, select: false });
      } catch {
        /* swallow — best-effort */
      }
    }
  }

  // -------------------------------------------------------- top-level

  private async topLevel(): Promise<Item[]> {
    const probe = await this.getProbe();
    const versionOk =
      !!probe.currentVersion && probe.installedVersions.includes(probe.currentVersion);
    const setupOk = probe.pythonOk && probe.ruffOk && probe.dockerOk && probe.caveOk && versionOk;
    const isCommActive = vscode.window.activeTextEditor?.document.languageId === 'comm';

    const setup = this.setupGroup(probe);
    const actions = this.actionsGroup();
    const versions = this.versionsGroup(probe);
    const settings = this.settingsGroup();

    const groups: Item[] = [];
    // 0. Setup at top when something needs attention.
    if (!setupOk) {
      groups.push(setup);
    }
    // 1. Quick actions — always.
    groups.push(actions);
    // 2. Command browser — only when a .comm file is active.
    if (isCommActive) {
      groups.push(this.commandBrowserGroup(probe));
    }
    // 3–4. Versions and settings (both collapsed).
    groups.push(versions, settings);
    // 5. Setup near the bottom when healthy. Out of the way but
    //    still glanceable via the n/5 counter in its title.
    if (setupOk) {
      groups.push(setup);
    }
    // 6. External links — out-of-band actions that don't need
    //    in-extension UI. Always last, always expanded.
    groups.push(this.externalGroup());
    return groups;
  }

  // ---------------------------------------------------------- External

  private externalGroup(): Item {
    const item = new Item('External', vscode.TreeItemCollapsibleState.Expanded);
    item.iconPath = new vscode.ThemeIcon('link');
    // VS Code doesn't apply theme foreground to custom-SVG iconPaths, so
    // ship two near-foreground variants (light = #424242, dark = #cccccc)
    // and let the renderer pick.
    const codeAsterIcon = {
      light: vscode.Uri.file(this.context.asAbsolutePath('media/images/code-aster-icon-light.svg')),
      dark: vscode.Uri.file(this.context.asAbsolutePath('media/images/code-aster-icon-dark.svg')),
    };

    const link = (
      label: string,
      icon: string | vscode.Uri | { light: vscode.Uri; dark: vscode.Uri },
      url: string
    ): Item => {
      const it = new Item(label);
      it.iconPath = typeof icon === 'string' ? new vscode.ThemeIcon(icon) : icon;
      it.tooltip = url;
      it.command = {
        title: label,
        command: 'vscode.open',
        arguments: [vscode.Uri.parse(url)],
      };
      return it;
    };

    item.children = [
      link('Star on GitHub', 'star-empty', 'https://github.com/simvia-tech/vs-code-aster'),
      link(
        'Rate on VS Code Marketplace',
        'feedback',
        'https://marketplace.visualstudio.com/items?itemName=simvia.vs-code-aster&ssr=false#review-details'
      ),
      link('Browse code_aster website', codeAsterIcon, 'https://www.code-aster.org/'),
      link(
        'Browse code_aster documentation',
        'library',
        'https://demo-docaster.simvia-app.fr/versions/v17/'
      ),
      link('Visit simvia.tech', 'globe', 'https://simvia.tech/'),
    ];
    return item;
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
        inFile: { ...EMPTY_FAMILIES },
        catalog: { ...EMPTY_FAMILIES },
        catalogLoaded: false,
      }
    );
  }

  private async runProbes(): Promise<void> {
    const [pythonResult, ruffOk, dockerOk, caveOk, installed, families] = await Promise.all([
      probeLspDeps(this.context),
      probeRuff(this.context),
      dockerAvailable(),
      caveOnPath(),
      listInstalledVersions(),
      this.fetchCommandFamilies(),
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
      inFile: families.inFile,
      catalog: families.catalog,
      catalogLoaded: families.catalogLoaded,
    };
  }

  /** Talk to the LSP to fill the Command browser group's data. Catalog
   * data is cached forever; in-file data is re-fetched per refresh. */
  private _catalogCache: CommandFamilies | null = null;
  private async fetchCommandFamilies(): Promise<{
    inFile: CommandFamilies;
    catalog: CommandFamilies;
    catalogLoaded: boolean;
  }> {
    let client: any;
    try {
      client = LspServer.instance.client;
    } catch {
      return {
        inFile: { ...EMPTY_FAMILIES },
        catalog: { ...EMPTY_FAMILIES },
        catalogLoaded: false,
      };
    }
    if (!client || !client.isRunning?.()) {
      return {
        inFile: { ...EMPTY_FAMILIES },
        catalog: { ...EMPTY_FAMILIES },
        catalogLoaded: false,
      };
    }
    // Catalog: fetch once, cache for the session.
    if (!this._catalogCache) {
      try {
        this._catalogCache =
          (await client.sendRequest('codeaster/getCompleteFamilies', {})) ?? null;
      } catch {
        this._catalogCache = null;
      }
    }
    // In-file: scoped to the active editor.
    let inFile: CommandFamilies = { ...EMPTY_FAMILIES };
    const editor = vscode.window.activeTextEditor;
    if (editor && editor.document.languageId === 'comm') {
      try {
        const result = await client.sendRequest('codeaster/analyzeCommandFamilies', {
          uri: editor.document.uri.toString(),
        });
        if (result && typeof result === 'object') {
          inFile = { ...EMPTY_FAMILIES, ...(result as Partial<CommandFamilies>) };
        }
      } catch {
        /* keep defaults */
      }
    }
    return {
      inFile,
      catalog: this._catalogCache ?? { ...EMPTY_FAMILIES },
      catalogLoaded: this._catalogCache !== null,
    };
  }

  // ------------------------------------------------------------ Setup

  private setupGroup(p: Probe): Item {
    const versionOk = !!p.currentVersion && p.installedVersions.includes(p.currentVersion);
    const checks = [p.pythonOk, p.ruffOk, p.dockerOk, p.caveOk, versionOk];
    const passed = checks.filter(Boolean).length;
    const allOk = passed === checks.length;
    const item = new Item(
      `Setup (${passed}/${checks.length})`,
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

    // Filter actions to whatever makes sense for the active editor.
    // Skip the file-specific ones rather than showing them grayed-out.
    const activeLang = vscode.window.activeTextEditor?.document.languageId;
    const activePath = vscode.window.activeTextEditor?.document.uri.fsPath ?? '';
    const isExport = activeLang === 'export';
    // Mesh viewer is the editor-title button on .comm files and .med
    // siblings (.mmed/.rmed plus user-configured numeric variants in
    // `vs-code-aster.medFileExtensions`). Mirror the same rule here.
    const medExts = new Set(
      vscode.workspace
        .getConfiguration('vs-code-aster')
        .get<string[]>('medFileExtensions', ['.med', '.mmed', '.rmed'])
        .map((e) => e.toLowerCase())
    );
    const ext = activePath.includes('.') ? activePath.slice(activePath.lastIndexOf('.')) : '';
    const isMeshViewable = activeLang === 'comm' || medExts.has(ext.toLowerCase());

    const children: Item[] = [
      this.actionItem('New export file…', 'new-file', 'vs-code-aster.exportDoc'),
    ];
    if (isExport) {
      children.push(this.actionItem('Run with code_aster', 'play', 'vs-code-aster.run-aster'));
    }
    if (isMeshViewable) {
      children.push(this.actionItem('Open mesh viewer', 'eye', 'vs-code-aster.meshViewer'));
    }
    children.push(
      this.actionItem('Restart language server', 'sync', 'vs-code-aster.restartLSPServer'),
      this.actionItem('Show catalog info', 'info', 'vs-code-aster.showCatalogInfo')
    );
    item.children = children;
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
    const item = new Item('Versions', vscode.TreeItemCollapsibleState.Collapsed);
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

  // ---------------------------------------------------- Command browser

  /** Identity-stable reference to the Command browser group, so the
   * status-bar click can `reveal()` it. Replaced on every refresh. */
  private _commandBrowserItem: Item | null = null;

  private commandBrowserGroup(p: Probe): Item {
    // Default to expanded whenever the user has a `.comm` file open —
    // that's the context where the dictionary is useful. Otherwise
    // collapsed so it doesn't crowd the panel.
    const expanded =
      vscode.window.activeTextEditor?.document.languageId === 'comm'
        ? vscode.TreeItemCollapsibleState.Expanded
        : vscode.TreeItemCollapsibleState.Collapsed;
    const item = new Item('Command browser', expanded);
    item.iconPath = new vscode.ThemeIcon('book');
    item.tooltip = 'code_aster commands grouped by family';
    item.contextValue = 'commandBrowser';
    this._commandBrowserItem = item;

    if (!p.catalogLoaded) {
      const placeholder = new Item('Loading catalog…');
      placeholder.iconPath = new vscode.ThemeIcon('sync~spin');
      item.children = [placeholder];
      return item;
    }

    item.children = FAMILIES.map((f) => {
      const inFile = new Set(p.inFile[f.key] ?? []);
      const all = p.catalog[f.key] ?? [];
      const family = new Item(f.label, vscode.TreeItemCollapsibleState.Collapsed);
      family.iconPath = new vscode.ThemeIcon(
        inFile.size > 0 ? 'pass-filled' : 'circle-outline',
        inFile.size > 0 ? new vscode.ThemeColor('testing.iconPassed') : undefined
      );
      family.description =
        all.length === 0
          ? 'no commands'
          : inFile.size === 0
            ? `${all.length} total`
            : `${inFile.size} in file · ${all.length} total`;
      const inFileSorted = [...inFile].sort();
      const restSorted = all.filter((n) => !inFile.has(n)).sort();
      family.children = [
        ...inFileSorted.map((n) => this._commandItem(n, true)),
        ...restSorted.map((n) => this._commandItem(n, false)),
      ];
      return family;
    });
    return item;
  }

  private _commandItem(name: string, inFile: boolean): Item {
    const it = new Item(name);
    it.iconPath = new vscode.ThemeIcon(
      inFile ? 'check' : 'symbol-method',
      inFile ? new vscode.ThemeColor('testing.iconPassed') : undefined
    );
    it.description = inFile ? 'in file' : undefined;
    it.tooltip = inFile ? `${name} — used in this file` : `${name} — open documentation`;
    it.command = {
      title: 'Open documentation',
      command: 'vs-code-aster.commandBrowser.openDoc',
      arguments: [name],
    };
    return it;
  }

  private settingsGroup(): Item {
    const item = new Item('Settings', vscode.TreeItemCollapsibleState.Collapsed);
    item.iconPath = new vscode.ThemeIcon('settings-gear');
    item.children = [
      this.settingItem('Python interpreter', 'vs-code-aster.pythonExecutablePath', 'terminal'),
      this.settingItem('Formatter', 'vs-code-aster.formatter', 'wand'),
      this.settingItem('Run alias', 'vs-code-aster.aliasForRun', 'play'),
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
  // createTreeView (not registerTreeDataProvider) gives us a TreeView
  // handle whose .reveal() can expand a specific item.
  const treeView = vscode.window.createTreeView(VIEW_ID, {
    treeDataProvider: provider,
    showCollapseAll: true,
  });
  provider.treeView = treeView;
  context.subscriptions.push(
    treeView,
    vscode.commands.registerCommand('vs-code-aster.sidebar.refresh', () => provider.refresh()),
    vscode.commands.registerCommand('vs-code-aster.commandBrowser.openDoc', (name: string) => {
      const url = `https://demo-docaster.simvia-app.fr/versions/v17/search.html?q=${encodeURIComponent(name)}`;
      void vscode.env.openExternal(vscode.Uri.parse(url));
    }),
    vscode.commands.registerCommand('vs-code-aster.commandBrowser.search', () =>
      runCommandSearch(provider)
    ),
    vscode.commands.registerCommand('vs-code-aster.commandBrowser.focus', () =>
      provider.revealCommandBrowser()
    )
  );
  return provider;
}

async function runCommandSearch(provider: SidebarProvider): Promise<void> {
  // Reuse the provider's cached catalog to avoid re-querying the LSP.
  const flat = await provider.flatCatalog();
  if (flat.length === 0) {
    vscode.window.showWarningMessage('Catalog is not yet available.');
    return;
  }
  const items: vscode.QuickPickItem[] = flat.map((c) => ({
    label: c.name,
    description: c.familyLabel,
  }));
  const picked = await vscode.window.showQuickPick(items, {
    placeHolder: 'Search code_aster commands by name…',
    matchOnDescription: true,
  });
  if (!picked) {
    return;
  }
  void vscode.commands.executeCommand('vs-code-aster.commandBrowser.openDoc', picked.label);
}
