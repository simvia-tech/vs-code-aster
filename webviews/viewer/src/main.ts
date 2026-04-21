import { mount } from 'svelte';
import App from './components/layout/App.svelte';
import { Controller } from './lib/Controller';
import { VisibilityManager } from './lib/commands/VisibilityManager';
import { CameraManager } from './lib/interaction/CameraManager';
import { GlobalSettings } from './lib/settings/GlobalSettings';
import { settings, errorMessage } from './lib/state';
import type { EdgeMode, SidebarSort } from './lib/state';
import './app.css';

declare function acquireVsCodeApi(): {
  postMessage(msg: unknown): void;
  getState(): unknown;
  setState(state: unknown): void;
};

const vscode = acquireVsCodeApi();
const scene = document.getElementById('scene')!;

mount(App, { target: document.getElementById('app')! });

Controller.Instance.init(scene, vscode);

window.addEventListener('message', async (e) => {
  const { type, body } = e.data;

  switch (type) {
    case 'init': {
      Controller.Instance.loadFiles(body.fileContexts, body.objFilenames);
      if (body.settings) {
        const s = body.settings;
        if (s.hiddenObjectOpacity !== undefined)
          GlobalSettings.Instance.hiddenObjectOpacity = s.hiddenObjectOpacity;
        if (s.edgeMode !== undefined) GlobalSettings.Instance.edgeMode = s.edgeMode as EdgeMode;
        if (s.edgeThresholdMultiplier !== undefined)
          GlobalSettings.Instance.edgeThresholdMultiplier = s.edgeThresholdMultiplier;
        if (s.edgeGroupThickness !== undefined)
          GlobalSettings.Instance.edgeGroupThickness = s.edgeGroupThickness;
        if (s.edgeGroupDepthOffset !== undefined)
          GlobalSettings.Instance.edgeGroupDepthOffset = s.edgeGroupDepthOffset;
        if (s.nodeGroupSize !== undefined) GlobalSettings.Instance.nodeGroupSize = s.nodeGroupSize;
        if (s.sidebarSort !== undefined)
          GlobalSettings.Instance.sidebarSort = s.sidebarSort as SidebarSort;
        if (s.groupByKind !== undefined) GlobalSettings.Instance.groupByKind = s.groupByKind;
        if (s.groupTransparency !== undefined)
          GlobalSettings.Instance.groupTransparency = s.groupTransparency;
        if (s.showOrientationWidget !== undefined)
          GlobalSettings.Instance.showOrientationWidget = s.showOrientationWidget;
        if (s.showBoundingBox !== undefined)
          GlobalSettings.Instance.showBoundingBox = s.showBoundingBox;
        if (s.showWireframe !== undefined) GlobalSettings.Instance.showWireframe = s.showWireframe;
        settings.update((cur) => ({
          hiddenObjectOpacity: s.hiddenObjectOpacity ?? cur.hiddenObjectOpacity,
          edgeMode: (s.edgeMode ?? cur.edgeMode) as EdgeMode,
          edgeThresholdMultiplier: s.edgeThresholdMultiplier ?? cur.edgeThresholdMultiplier,
          edgeGroupThickness: s.edgeGroupThickness ?? cur.edgeGroupThickness,
          edgeGroupDepthOffset: s.edgeGroupDepthOffset ?? cur.edgeGroupDepthOffset,
          nodeGroupSize: s.nodeGroupSize ?? cur.nodeGroupSize,
          sidebarSort: (s.sidebarSort ?? cur.sidebarSort) as SidebarSort,
          groupByKind: s.groupByKind ?? cur.groupByKind,
          groupTransparency: s.groupTransparency ?? cur.groupTransparency,
          showOrientationWidget: s.showOrientationWidget ?? cur.showOrientationWidget,
          showBoundingBox: s.showBoundingBox ?? cur.showBoundingBox,
          showWireframe: s.showWireframe ?? cur.showWireframe,
        }));
        VisibilityManager.Instance.applyHiddenObjectOpacity();
        CameraManager.Instance.refreshEdgeVisibility();
        if (s.showOrientationWidget === false) {
          CameraManager.Instance.setOrientationWidgetVisible(false);
        }
        if (s.showBoundingBox === true) {
          CameraManager.Instance.setBoundingBoxVisible(true);
        }
        if (s.showWireframe === true) {
          CameraManager.Instance.setWireframeMode(true);
        }
      }
      break;
    }

    case 'displayGroup':
      VisibilityManager.Instance.setVisibility(body.group, body.visible);
      break;

    case 'showOnlyObjects':
      VisibilityManager.Instance.showOnlyObjects(body.objects);
      break;

    case 'error':
      errorMessage.set(body?.message || 'An error occurred.');
      break;
  }
});

vscode.postMessage({ type: 'ready' });
