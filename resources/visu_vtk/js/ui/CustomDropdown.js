/**
 * A reusable custom dropdown that matches the VS Code Aster UI style.
 * The panel is appended to document.body to avoid overflow clipping.
 */
class CustomDropdown {
  /**
   * @param {HTMLElement} trigger - Element that opens/closes the panel on click
   * @param {{ value: string, label: string }[]} options
   * @param {(value: string) => void} onSelect - Called when the user picks an option
   * @param {() => string|null} getValue - Returns the currently selected value (shown with a checkmark)
   * @param {{ align?: 'left'|'right' }} [opts]
   */
  constructor(trigger, options, onSelect, getValue, opts = {}) {
    this._trigger = trigger;
    this._options = options;
    this._onSelect = onSelect;
    this._getValue = getValue;
    this._align = opts.align ?? 'left';
    this._panel = null;

    trigger.addEventListener('click', (e) => {
      e.stopPropagation();
      this._panel ? this._close() : this._open();
    });
    document.addEventListener('click', () => this._close());
  }

  _open() {
    const currentValue = this._getValue?.();

    const panel = document.createElement('div');
    panel.style.cssText = `
      position: fixed;
      z-index: 9999;
      background: var(--ui-popup-bg);
      border: 1px solid var(--ui-border);
      border-radius: 4px;
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
      padding: 3px 0;
      overflow: hidden;
    `;
    panel.addEventListener('click', (e) => e.stopPropagation());

    const showCheckmarks = this._getValue != null;

    this._options.forEach(({ value, label }) => {
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

      const labelEl = document.createElement('span');
      labelEl.textContent = label;

      if (showCheckmarks) {
        const check = document.createElement('span');
        check.textContent = '✓';
        check.style.cssText = `
          font-size: 0.6rem;
          flex-shrink: 0;
          width: 10px;
          opacity: ${isSelected ? 1 : 0};
        `;
        item.appendChild(check);
      }

      item.appendChild(labelEl);

      item.addEventListener('mouseenter', () => {
        item.style.background = 'var(--ui-element-bg-hover)';
      });
      item.addEventListener('mouseleave', () => {
        item.style.background = '';
      });
      item.addEventListener('click', () => {
        this._onSelect(value);
        this._close();
      });

      panel.appendChild(item);
    });

    document.body.appendChild(panel);

    // Position after append so dimensions are known
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

  _close() {
    this._panel?.remove();
    this._panel = null;
  }
}
