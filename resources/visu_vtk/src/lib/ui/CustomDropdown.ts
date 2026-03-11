export interface DropdownOption {
  value: string;
  label: string;
}

export class CustomDropdown {
  private _trigger: HTMLElement;
  private _options: DropdownOption[];
  private _onSelect: (value: string) => void;
  private _getValue: (() => string | null) | null;
  private _align: 'left' | 'right';
  private _panel: HTMLElement | null = null;

  constructor(
    trigger: HTMLElement,
    options: DropdownOption[],
    onSelect: (value: string) => void,
    getValue: (() => string | null) | null = null,
    opts: { align?: 'left' | 'right' } = {},
  ) {
    this._trigger = trigger;
    this._options = options;
    this._onSelect = onSelect;
    this._getValue = getValue;
    this._align = opts.align ?? 'left';

    trigger.addEventListener('click', (e) => {
      e.stopPropagation();
      this._panel ? this.close() : this._open();
    });
    document.addEventListener('click', () => this.close());
  }

  private _open(): void {
    const currentValue = this._getValue?.();
    const showCheckmarks = this._getValue != null;

    const panel = document.createElement('div');
    panel.style.cssText = `
      position: fixed;
      z-index: 9999;
      background: var(--ui-popup-bg);
      border: 1px solid var(--ui-border);
      border-radius: 4px;
      box-shadow: 0 4px 16px rgba(0,0,0,0.25);
      padding: 3px 0;
      overflow: hidden;
    `;
    panel.addEventListener('click', (e) => e.stopPropagation());

    for (const { value, label } of this._options) {
      const isSelected = value === currentValue;
      const item = document.createElement('div');
      item.style.cssText = `
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 5px 10px;
        font-size: 0.75rem;
        cursor: pointer;
        color: var(--ui-fg);
        white-space: nowrap;
        ${this._align === 'right' ? 'justify-content: flex-end;' : ''}
        ${isSelected ? 'font-weight: 600;' : ''}
      `;

      if (showCheckmarks) {
        const check = document.createElement('span');
        check.textContent = '✓';
        check.style.cssText = `font-size: 0.6rem; flex-shrink: 0; width: 10px; opacity: ${isSelected ? 1 : 0};`;
        item.appendChild(check);
      }

      const labelEl = document.createElement('span');
      labelEl.textContent = label;
      item.appendChild(labelEl);

      item.addEventListener('mouseenter', () => { item.style.background = 'var(--ui-element-bg-hover)'; });
      item.addEventListener('mouseleave', () => { item.style.background = ''; });
      item.addEventListener('click', () => { this._onSelect(value); this.close(); });

      panel.appendChild(item);
    }

    document.body.appendChild(panel);

    const rect = this._trigger.getBoundingClientRect();
    const panelW = Math.max(panel.offsetWidth, rect.width);
    const panelH = panel.offsetHeight;
    panel.style.minWidth = `${panelW}px`;

    let left = rect.left + rect.width / 2 - panelW / 2;
    left = Math.max(4, Math.min(left, window.innerWidth - panelW - 4));
    panel.style.left = `${left}px`;

    const openUp = window.innerHeight - rect.bottom < panelH + 8;
    panel.style.top = openUp
      ? `${rect.top - panelH - 4}px`
      : `${rect.bottom + 4}px`;

    this._panel = panel;
  }

  close(): void {
    this._panel?.remove();
    this._panel = null;
  }
}
