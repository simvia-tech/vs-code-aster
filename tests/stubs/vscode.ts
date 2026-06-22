/**
 * Faithful, minimal stand-in for the `vscode` module, used as a Vitest
 * `resolve.alias` target in the `unit` project. It implements only the runtime
 * values that pure extension-host logic constructs (Uri / Position / Range /
 * Diagnostic / DiagnosticSeverity / Location / EventEmitter). Anything not
 * exercised by a unit-tested code path can stay unimplemented — add to it as
 * new pure modules come under test.
 *
 * This file is never bundled into the extension; production code uses the real
 * `vscode` module provided by the extension host.
 */

export enum DiagnosticSeverity {
  Error = 0,
  Warning = 1,
  Information = 2,
  Hint = 3,
}

export class Position {
  constructor(
    public readonly line: number,
    public readonly character: number
  ) {}

  isEqual(other: Position): boolean {
    return this.line === other.line && this.character === other.character;
  }
}

export class Range {
  public readonly start: Position;
  public readonly end: Position;

  constructor(start: Position, end: Position);
  constructor(startLine: number, startChar: number, endLine: number, endChar: number);
  constructor(a: Position | number, b: Position | number, c?: number, d?: number) {
    if (typeof a === 'number') {
      this.start = new Position(a, b as number);
      this.end = new Position(c as number, d as number);
    } else {
      this.start = a;
      this.end = b as Position;
    }
  }

  get isEmpty(): boolean {
    return this.start.isEqual(this.end);
  }
}

export class Diagnostic {
  public source?: string;
  public code?: string | number;
  public relatedInformation?: unknown[];

  constructor(
    public range: Range,
    public message: string,
    public severity: DiagnosticSeverity = DiagnosticSeverity.Error
  ) {}
}

export class Location {
  constructor(
    public readonly uri: Uri,
    public readonly range: Range
  ) {}
}

/**
 * Small URI implementation good enough for `toString()` identity (used as Map
 * keys) and `fsPath`. Not a full RFC 3986 parser.
 */
export class Uri {
  private constructor(
    public readonly scheme: string,
    public readonly authority: string,
    public readonly path: string,
    public readonly query = '',
    public readonly fragment = ''
  ) {}

  static file(fsPath: string): Uri {
    let p = fsPath.replace(/\\/g, '/');
    if (!p.startsWith('/')) {
      p = '/' + p;
    }
    return new Uri('file', '', p);
  }

  static parse(value: string): Uri {
    const match = /^(\w[\w+.-]*):(?:\/\/([^/?#]*))?([^?#]*)(?:\?([^#]*))?(?:#(.*))?$/.exec(value);
    if (!match) {
      return new Uri('file', '', value);
    }
    return new Uri(match[1], match[2] ?? '', match[3] ?? '', match[4] ?? '', match[5] ?? '');
  }

  get fsPath(): string {
    return this.path;
  }

  with(change: {
    scheme?: string;
    authority?: string;
    path?: string;
    query?: string;
    fragment?: string;
  }): Uri {
    return new Uri(
      change.scheme ?? this.scheme,
      change.authority ?? this.authority,
      change.path ?? this.path,
      change.query ?? this.query,
      change.fragment ?? this.fragment
    );
  }

  toString(): string {
    let result = `${this.scheme}://${this.authority}${this.path}`;
    if (this.query) {
      result += `?${this.query}`;
    }
    if (this.fragment) {
      result += `#${this.fragment}`;
    }
    return result;
  }
}

type Listener<T> = (e: T) => unknown;

export class EventEmitter<T> {
  private listeners: Listener<T>[] = [];

  event = (listener: Listener<T>) => {
    this.listeners.push(listener);
    return {
      dispose: () => {
        this.listeners = this.listeners.filter((l) => l !== listener);
      },
    };
  };

  fire(data: T): void {
    for (const l of this.listeners) {
      l(data);
    }
  }

  dispose(): void {
    this.listeners = [];
  }
}

export class ThemeIcon {
  constructor(public readonly id: string) {}
}

export const workspace = {
  getConfiguration: () => ({
    get: (_key: string, fallback?: unknown) => fallback,
  }),
};

export const window = {
  showErrorMessage: () => Promise.resolve(undefined),
  showWarningMessage: () => Promise.resolve(undefined),
  showInformationMessage: () => Promise.resolve(undefined),
  createOutputChannel: () => ({
    appendLine: () => {},
    append: () => {},
    show: () => {},
    dispose: () => {},
  }),
};

export const commands = {
  registerCommand: () => ({ dispose: () => {} }),
  executeCommand: () => Promise.resolve(undefined),
};
