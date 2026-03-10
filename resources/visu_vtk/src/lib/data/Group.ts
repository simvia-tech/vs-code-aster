import { GlobalSettings } from '../settings/GlobalSettings';

export class Group {
  actor: any;
  name: string;
  isFaceGroup: boolean;
  fileGroup: string | null;
  size: number | null;
  colorIndex: number | null;
  isObjectActor: boolean;
  cellCount: number | null;
  private _edgeT?: number;

  constructor(
    actor: any,
    name: string,
    isFaceGroup: boolean,
    fileGroup: string | null = null,
    parentSize: number | null = null,
    colorIndex: number | null = null,
    isObjectActor = false,
    cellCount: number | null = null,
  ) {
    this.actor = actor;
    this.name = name;
    this.isFaceGroup = isFaceGroup;
    this.fileGroup = fileGroup;
    this.size = parentSize;
    this.colorIndex = colorIndex;
    this.isObjectActor = isObjectActor;
    this.cellCount = cellCount;
  }

  applyThemeColor(): void {
    if (this.colorIndex === null) return;
    const colors = this.isObjectActor
      ? GlobalSettings.Instance.objectColors
      : GlobalSettings.Instance.meshGroupColors;
    const color = colors[this.colorIndex % colors.length];
    this.actor.getProperty().setColor(color);
    this._applyEdgeColor();
  }

  updateEdgeVisibility(currentDistance: number, initialDistance: number): void {
    if (this.cellCount === null) return;
    const prop = this.actor.getProperty();
    const mode = GlobalSettings.Instance.edgeMode;

    if (mode === 'hide') {
      prop.setEdgeVisibility(false);
      return;
    }
    if (mode === 'show') {
      prop.setEdgeVisibility(true);
      prop.setEdgeColor(0, 0, 0);
      return;
    }

    const threshold = initialDistance * Math.sqrt(15000 / this.cellCount) * GlobalSettings.Instance.edgeThresholdMultiplier;

    if (mode === 'threshold') {
      prop.setEdgeVisibility(currentDistance < threshold);
      prop.setEdgeColor(0, 0, 0);
      return;
    }

    prop.setEdgeVisibility(true);
    this._edgeT = Math.min(1, Math.max(0, threshold / currentDistance));
    this._applyEdgeColor();
  }

  private _applyEdgeColor(): void {
    const t = this._edgeT ?? 0;
    const [r, g, b] = this.actor.getProperty().getColor();
    this.actor.getProperty().setEdgeColor(r * (1 - t), g * (1 - t), b * (1 - t));
  }

  setSize(distance: number): void {
    const decay = (this.size ?? 1) / 5;
    const scale = Math.max(30 * (1 / Math.sqrt(1 + distance / decay)), 0);
    this.actor.getProperty().setPointSize(scale);
  }

  getColor(): number[] {
    return this.actor.getProperty().getColor();
  }

  setVisibility(visible: boolean): void {
    this.actor.setVisibility(visible);
  }

  setOpacity(opacity: number): void {
    this.actor.getProperty().setOpacity(opacity);
  }
}
