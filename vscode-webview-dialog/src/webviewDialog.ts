import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';

/**
 * Provides basic "dialog" semantics over a VS Code webview panel.
 *
 * The contents of the dialog must be provided as HTML; the HTML should include script that
 * sends messages.
 */
export class WebviewDialog<TResult> implements vscode.Disposable {
	private result?: TResult;

	public readonly panel: vscode.WebviewPanel;
	public get webview(): vscode.Webview { return this.panel.webview; }

	/**
	 * Constructs a new webview dialog. The dialog is shown as soon as
	 * it is constructed.
	 *
	 * The dialog instance may only be used once. It may not be re-shown
	 * after it is closed; create another instance instead.
	 */
	public constructor(
		viewType: string,
		resourceRootDir: string,
		dialogHtmlFileName: string,
		viewColumn?: vscode.ViewColumn,
	) {
		viewColumn = viewColumn || vscode.ViewColumn.Beside;
		const options: vscode.WebviewOptions | vscode.WebviewPanelOptions = {
			enableScripts: true,
			localResourceRoots: [
				vscode.Uri.file(resourceRootDir),
			]
		};

		const dialogHtmlFile = path.join(resourceRootDir, dialogHtmlFileName);
		let html = fs.readFileSync(dialogHtmlFile, { encoding: 'utf8' });

		const title = this.extractHtmlTitle(html, 'Dialog');

		this.panel = vscode.window.createWebviewPanel(
			viewType,
			title,
			viewColumn,
			options);

		html = this.fixResourceReferences(html, resourceRootDir);
		html = this.fixCspSourceReferences(html);
		this.panel.webview.html = html;

		this.panel.webview.onDidReceiveMessage((message) => {
			if (message.command === 'cancel') {
				this.panel.dispose();
			} else if (message.command === 'result') {
				this.result = message.value as TResult;
				this.panel.dispose();
			}
		});

		this.panel.webview.onDidReceiveMessage(message => {
	if (message.command === 'autocomplete') {
		vscode.window.showInformationMessage("Entrée reçue : " + message.value);

		try {
			const suggestions = this.getMatchingFiles(message.value);
			vscode.window.showInformationMessage("Suggestions calculées !");
			/** A FAIRE : debuger getmatchingfgile, derrière balader l'input dans les message,
			 * après on peut fiare le htmt, et si on est des malades, faire un trcu de controle 
			 * dans le menu de controle (au clic, ou avec les fleches (va falloir boswer))
			 */
				vscode.window.showInformationMessage(
				`Entrée en cours : "$inputValue}"\nSuggestions : ${suggestions.join(', ') || '(aucune)'}`
			);
			// this.panel.webview.postMessage({ command: 'autocompleteResult', suggestions });
		} catch (err) {
			vscode.window.showInformationMessage("Erreur dans getMatchingFiles: ");
		}
	}
});

	}

	private getMatchingFiles(partial: string): string[] {
		const dir = vscode.workspace.workspaceFolders?.[0].uri.fsPath;
		if (!dir) return [];

		const allFiles = fs.readdirSync(dir);
		return allFiles.filter(name => name.includes(partial));
	}

	/**
	 * Extract the dialog title from the <title> tag of the HTML.
	 */
	private extractHtmlTitle(html: string, defaultTitle: string): string {
		const titleMatch = /\<title\>([^<]*)\<\/title\>/.exec(html);
		const title = (titleMatch && titleMatch[1]) || defaultTitle;
		return title;
	}

	/**
	 * Replace references to href="./file" or src="./file" with VS Code resource URIs.
	 */
	private fixResourceReferences(html: string, resourceRootDir: string): string {
		const refRegex = /((href)|(src))="(\.\/[^"]+)"/g;
		let refMatch;
		while ((refMatch = refRegex.exec(html)) !== null) {
			const offset = refMatch.index;
			const length = refMatch[0].length;
			const refAttr = refMatch[1];
			const refName = refMatch[4];
			const refPath = path.join(resourceRootDir, refName);
			const refUri = this.webview.asWebviewUri(vscode.Uri.file(refPath));
			const refReplace = refAttr + "=\"" + refUri + "\"";
			html = html.slice(0, offset) + refReplace + html.slice(offset + length);
		}
		return html;
	}

	/**
	 * Replace references to ${webview.cspSource} with the actual value.
	 */
	private fixCspSourceReferences(html: string): string {
		const cspSourceRegex = /\${webview.cspSource}/g;
		let cspSourceMatch;
		while ((cspSourceMatch = cspSourceRegex.exec(html)) !== null) {
			html = html.slice(0, cspSourceMatch.index) + this.webview.cspSource +
				html.slice(cspSourceMatch.index + cspSourceMatch[0].length);
		}

		return html;
	}

	/**
	 * Waits for the dialog to close, then gets the result, or `null`
	 * if the dialog was cancelled.
	 * @param cancellation Optional cancellation token that can be used to
	 * cancel waiting on a result. Cancelling the token also closes the dialog.
	 */
	public async getResult(
		cancellation?: vscode.CancellationToken,
	): Promise<TResult | null> {
		const disposePromise = new Promise<void>((resolve, reject) => {
			this.panel.onDidDispose(resolve);
		});

		let cancellationRegistration: vscode.Disposable | undefined;
		if (cancellation) {
			cancellationRegistration = cancellation.onCancellationRequested(() => {
				this.panel.dispose();
			});
		}

		await disposePromise;

		if (cancellationRegistration) {
			cancellationRegistration.dispose();
		}

		return this.result === undefined ? null : this.result;
	}

	public dispose() {
		this.panel.dispose();
	}
}
