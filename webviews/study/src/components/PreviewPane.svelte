<script lang="ts">
  let { comm, exportText, baseName }: { comm: string; exportText: string; baseName: string } =
    $props();

  let tab = $state<'comm' | 'export'>('comm');

  type Tok = { text: string; cls: string };

  // Comments, strings, command/factor names (IDENT before "("), keyword
  // arguments (IDENT before "="), and numbers. Good enough for the generated
  // .comm (Python-like) and .export, which we control.
  const TOKEN_RE =
    /(#.*)|("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')|([A-Za-z_][A-Za-z0-9_]*)(?=\s*\()|([A-Za-z_][A-Za-z0-9_]*)(?=\s*=(?!=))|(-?\d+\.?\d*(?:[eE][+-]?\d+)?)/g;

  // Theme-aware colors via VS Code's exposed token/debug variables, with
  // sensible dark-theme fallbacks. Inline styles keep this CSP-safe and avoid
  // Svelte scoped-class pruning.
  const STYLE: Record<string, string> = {
    comment: 'color: var(--vscode-descriptionForeground, #6a9955); font-style: italic;',
    string: 'color: var(--vscode-debugTokenExpression-string, #ce9178);',
    number: 'color: var(--vscode-debugTokenExpression-number, #b5cea8);',
    function: 'color: var(--vscode-symbolIcon-functionForeground, #dcdcaa);',
    keyword:
      'color: var(--vscode-symbolIcon-keywordForeground, var(--vscode-debugTokenExpression-name, #9cdcfe));',
    plain: '',
  };

  function tokenize(line: string): Tok[] {
    const toks: Tok[] = [];
    let last = 0;
    TOKEN_RE.lastIndex = 0;
    let m: RegExpExecArray | null;
    while ((m = TOKEN_RE.exec(line)) !== null) {
      if (m.index > last) {
        toks.push({ text: line.slice(last, m.index), cls: 'plain' });
      }
      const cls = m[1]
        ? 'comment'
        : m[2]
          ? 'string'
          : m[3]
            ? 'function'
            : m[4]
              ? 'keyword'
              : 'number';
      toks.push({ text: m[0], cls });
      last = m.index + m[0].length;
      if (m[0].length === 0) {
        TOKEN_RE.lastIndex++;
      }
    }
    if (last < line.length) {
      toks.push({ text: line.slice(last), cls: 'plain' });
    }
    return toks;
  }

  const lines = $derived((tab === 'comm' ? comm : exportText).split('\n'));
</script>

<div class="flex h-full flex-col">
  <div class="flex gap-1 border-b border-ui-border">
    <button
      type="button"
      class="cursor-pointer px-3 py-1.5 text-sm {tab === 'comm'
        ? 'border-b-2 border-ui-btn font-medium'
        : 'text-ui-text-secondary'}"
      onclick={() => (tab = 'comm')}
    >
      {baseName}.comm
    </button>
    <button
      type="button"
      class="cursor-pointer px-3 py-1.5 text-sm {tab === 'export'
        ? 'border-b-2 border-ui-btn font-medium'
        : 'text-ui-text-secondary'}"
      onclick={() => (tab = 'export')}
    >
      {baseName}.export
    </button>
  </div>
  <pre
    class="m-0 flex-1 overflow-auto whitespace-pre p-3 font-mono text-xs leading-relaxed">{#each lines as line, i (i)}{#each tokenize(line) as t, j (j)}<span
          style={STYLE[t.cls]}>{t.text}</span
        >{/each}{#if i < lines.length - 1}{'\n'}{/if}{/each}</pre>
</div>
