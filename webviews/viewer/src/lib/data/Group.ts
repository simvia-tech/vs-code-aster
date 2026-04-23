import { GlobalSettings } from '../settings/GlobalSettings';
import type { GroupKind } from '../state';
export type { GroupKind };

export class Group {
  actor: any;
  name: string;
  kind: GroupKind;
  fileGroup: string | null;
  size: number | null;
  colorIndex: number | null;
  isObjectActor: boolean;
  cellCount: number | null;
  standaloneEdgesActor: any = null;
  standaloneEdgesContourActor: any = null;
  private _edgeT?: number;
  private _visible = true;
  private _opacity = 1;
  private _wireframe = false;
  private _edgeVisible = true;
  private _edgeFade = 1;

  constructor(
    actor: any,
    name: string,
    kind: GroupKind,
    fileGroup: string | null = null,
    parentSize: number | null = null,
    colorIndex: number | null = null,
    isObjectActor = false,
    cellCount: number | null = null
  ) {
    this.actor = actor;
    this.name = name;
    this.kind = kind;
    this.fileGroup = fileGroup;
    this.size = parentSize;
    this.colorIndex = colorIndex;
    this.isObjectActor = isObjectActor;
    this.cellCount = cellCount;
  }

  get isSurfaceGroup(): boolean {
    return this.kind === 'face' || this.kind === 'volume';
  }

  applyThemeColor(): void {
    if (this.colorIndex === null) return;
    const colors = this.isObjectActor
      ? GlobalSettings.Instance.objectColors
      : GlobalSettings.Instance.meshGroupColors;
    const color = colors[this.colorIndex % colors.length];
    this.actor.getProperty().setColor(color);
    if (this.standaloneEdgesActor) {
      this.standaloneEdgesActor.getProperty().setColor(color[0], color[1], color[2]);
    }
    this._applyEdgeColor();
  }

  updateEdgeVisibility(currentDistance: number, initialDistance: number): void {
    if (this.cellCount === null) return;
    const prop = this.actor.getProperty();
    const mode = GlobalSettings.Instance.edgeMode;

    if (mode === 'hide') {
      prop.setEdgeVisibility(false);
      this._edgeVisible = false;
      this._edgeFade = 0;
      this._updateStandaloneEdges();
      return;
    }
    if (mode === 'show') {
      prop.setEdgeVisibility(true);
      this._applyFlatEdgeColor(prop);
      this._edgeVisible = true;
      this._edgeFade = 1;
      this._updateStandaloneEdges();
      return;
    }

    const threshold =
      initialDistance *
      Math.sqrt(15000 / this.cellCount) *
      GlobalSettings.Instance.edgeThresholdMultiplier;

    if (mode === 'threshold') {
      const visible = currentDistance < threshold;
      prop.setEdgeVisibility(visible);
      this._applyFlatEdgeColor(prop);
      this._edgeVisible = visible;
      this._edgeFade = visible ? 1 : 0;
      this._updateStandaloneEdges();
      return;
    }

    prop.setEdgeVisibility(true);
    this._edgeT = Math.min(1, Math.max(0, threshold / currentDistance));
    this._applyEdgeColor();
    this._edgeVisible = true;
    this._edgeFade = this._edgeT;
    this._updateStandaloneEdges();
  }

  private _applyFlatEdgeColor(prop: any): void {
    const op = GlobalSettings.Instance.edgeOpacity;
    const [r, g, b] = prop.getColor();
    prop.setEdgeColor(r * (1 - op), g * (1 - op), b * (1 - op));
  }

  private _applyEdgeColor(): void {
    const t = this._edgeT ?? 0;
    const op = GlobalSettings.Instance.edgeOpacity;
    const [r, g, b] = this.actor.getProperty().getColor();
    this.actor.getProperty().setEdgeColor(r * (1 - t * op), g * (1 - t * op), b * (1 - t * op));
  }

  setSize(distance: number): void {
    const decay = (this.size ?? 1) / 5;
    const multiplier = GlobalSettings.Instance.nodeGroupSize;
    const scale = Math.max(30 * multiplier * (1 / Math.sqrt(1 + distance / decay)), 0);
    this.actor.getProperty().setPointSize(scale);
  }

  getColor(): number[] {
    return this.actor.getProperty().getColor();
  }

  setVisibility(visible: boolean): void {
    this._visible = visible;
    this.actor.setVisibility(visible);
    this._updateStandaloneEdges();
  }

  setOpacity(opacity: number): void {
    this._opacity = opacity;
    this.actor.getProperty().setOpacity(opacity);
    this._updateStandaloneEdges();
  }

  setWireframeMode(wireframe: boolean): void {
    this._wireframe = wireframe;
    this._updateStandaloneEdges();
  }

  private _updateStandaloneEdges(): void {
    if (!this.standaloneEdgesActor) return;
    const transparent = this._opacity < 1;
    const thin = transparent || this._wireframe;
    const lineOpacity = transparent ? this._opacity * 0.4 : this._opacity;
    this.standaloneEdgesActor.setVisibility(this._visible);
    this.standaloneEdgesActor.getProperty().setOpacity(lineOpacity);
    this.standaloneEdgesActor.getProperty().setLineWidth(thin ? 1 : 2);
    if (this.standaloneEdgesContourActor) {
      const contourVisible = this._visible && !thin && this._edgeVisible;
      this.standaloneEdgesContourActor.setVisibility(contourVisible);
      this.standaloneEdgesContourActor.getProperty().setOpacity(lineOpacity * this._edgeFade);
    }
  }
}
