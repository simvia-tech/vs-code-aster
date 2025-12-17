import * as vscode from 'vscode';
import { LspServer } from './LspServer';

interface CommandFamiliesAnalysis {
    mesh: string[];
    material: string[];
    bcAndLoads: string[];
    analysis: string[];
    output: string[];
}

type FamilyKey = keyof CommandFamiliesAnalysis;

export const COMMAND_FAMILIES: { key: FamilyKey; label: string }[] = [
    { key: 'mesh', label: 'Mesh' },
    { key: 'material', label: 'Material' },
    { key: 'bcAndLoads', label: 'Boundary Conditions & Loads' },
    { key: 'analysis', label: 'Analysis' },
    { key: 'output', label: 'Output' }
];

export class StatusBar {
    private static _instance: StatusBar | null = null;
    private statusBarItem: vscode.StatusBarItem;
    private currentAnalysis: CommandFamiliesAnalysis | null = null;
    private disposables: vscode.Disposable[] = [];
    private completeFamilies: CommandFamiliesAnalysis = {
        mesh: [],
        material: [],
        bcAndLoads: [],
        analysis: [],
        output: []
    };

    private constructor() {
        this.statusBarItem = vscode.window.createStatusBarItem(
            vscode.StatusBarAlignment.Left
        );
        this.statusBarItem.command = 'codeaster.showCommandFamiliesDetails';
        this.statusBarItem.tooltip = 'Click to see details';
    }

    public static get instance(): StatusBar {
        if (!StatusBar._instance) {
            StatusBar._instance = new StatusBar();
        }
        return StatusBar._instance;
    }

    /** Activate status bar and register listeners */
    public async activate(context: vscode.ExtensionContext) {
        await this.getCompleteFamilies();

        const showDetailsCommand = vscode.commands.registerCommand(
            'codeaster.showCommandFamiliesDetails',
            () => this.showDetails()
        );
        context.subscriptions.push(showDetailsCommand);

        const editorChangeListener = vscode.window.onDidChangeActiveTextEditor(
            editor => this.onEditorChange(editor)
        );
        this.disposables.push(editorChangeListener);

        this.onEditorChange(vscode.window.activeTextEditor);

        context.subscriptions.push(this.statusBarItem, ...this.disposables);
    }

    /** Update status bar visibility and trigger analysis on editor change */
    public async onEditorChange(editor: vscode.TextEditor | undefined) {
        if (!editor) {
            this.statusBarItem.hide();
            return;
        }

        const document = editor.document;
        if (document.languageId !== 'comm') {
            this.statusBarItem.hide();
            return;
        }

        this.statusBarItem.show();
        await this.analyzeDocument(document);
    }

    /** Fetch all command families from the LSP server */
    private async getCompleteFamilies() {
        try {
            const client = LspServer.instance.client;
            if (!client) {return;}

            const completeFamilies = await client.sendRequest<CommandFamiliesAnalysis>(
                'codeaster/getCompleteFamilies', {}
            );

            this.completeFamilies = completeFamilies;
        } catch (error) {
            console.error('Error fetching command families:', error);
        }
    }

    /** Analyze the current document and update status bar */
    private async analyzeDocument(document: vscode.TextDocument) {
        try {
            const client = LspServer.instance.client;
            if (!client) {
                this.statusBarItem.hide();
                return;
            }

            const analysis = await client.sendRequest<CommandFamiliesAnalysis>(
                'codeaster/analyzeCommandFamilies',
                { uri: document.uri.toString() }
            );

            this.currentAnalysis = analysis;
            this.updateStatusBarText(analysis);

        } catch (error) {
            console.error('Error analyzing command families:', error);
            this.statusBarItem.hide();
        }
    }

    /** Update the status bar text based on analysis result */
    private updateStatusBarText(analysis: CommandFamiliesAnalysis) {
        const completed = Object.values(analysis).filter(
            commands => Array.isArray(commands) && commands.length > 0
        ).length;

        const icon = completed === 5 ? '$(check)' : '$(info)';
        this.statusBarItem.text = `${icon} code_aster: ${completed}/5 steps`;
    }

    /** Show a QuickPick with detailed commands for each family */
    private async showDetails() {
        if (!this.currentAnalysis) {return;}

        const analysis = this.currentAnalysis;

        const items = COMMAND_FAMILIES.map(family => {
            const commands = analysis[family.key] || [];
            const icon = commands.length > 0 ? '$(check)' : '$(circle-slash)';
            const detail = commands.length > 0 ? `Commands: ${commands.join(', ')}` : 'No commands defined yet';
            return { label: `${icon} ${family.label}`, detail, key: family.key };
        });

        const selectedFamily = await vscode.window.showQuickPick(items, {
            placeHolder: 'code_aster command families: select a family to view commands'
        });

        if (!selectedFamily) {return;}

        const selectedKey = selectedFamily.key;
        const commands = this.completeFamilies[selectedKey] || [];
        if (commands.length === 0) {return;}

        const commandItems = commands.map(cmd => ({ label: `$(symbol-method) ${cmd}` }));
        await vscode.window.showQuickPick(commandItems, { placeHolder: `${selectedFamily.key} commands`, canPickMany: false });
    }

    /** Dispose status bar and listeners */
    public dispose() {
        this.statusBarItem.dispose();
        this.disposables.forEach(d => d.dispose());
    }
}
