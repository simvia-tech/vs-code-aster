import { mount } from 'svelte';
import App from './components/App.svelte';
import { Controller } from './lib/Controller';
import { VisibilityManager } from './lib/commands/VisibilityManager';
import { CameraManager } from './lib/interaction/CameraManager';
import { GlobalSettings } from './lib/settings/GlobalSettings';
import { settings } from './lib/state';
import type { EdgeMode } from './lib/state';
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
        if (s.hiddenObjectOpacity !== undefined) GlobalSettings.Instance.hiddenObjectOpacity = s.hiddenObjectOpacity;
        if (s.edgeMode !== undefined) GlobalSettings.Instance.edgeMode = s.edgeMode as EdgeMode;
        if (s.edgeThresholdMultiplier !== undefined) GlobalSettings.Instance.edgeThresholdMultiplier = s.edgeThresholdMultiplier;
        if (s.groupTransparency !== undefined) GlobalSettings.Instance.groupTransparency = s.groupTransparency;
        if (s.showOrientationWidget !== undefined) GlobalSettings.Instance.showOrientationWidget = s.showOrientationWidget;
        settings.update((cur) => ({
          hiddenObjectOpacity: s.hiddenObjectOpacity ?? cur.hiddenObjectOpacity,
          edgeMode: (s.edgeMode ?? cur.edgeMode) as EdgeMode,
          edgeThresholdMultiplier: s.edgeThresholdMultiplier ?? cur.edgeThresholdMultiplier,
          groupTransparency: s.groupTransparency ?? cur.groupTransparency,
          showOrientationWidget: s.showOrientationWidget ?? cur.showOrientationWidget,
        }));
        VisibilityManager.Instance.applyHiddenObjectOpacity();
        CameraManager.Instance.refreshEdgeVisibility();
        if (s.showOrientationWidget === false) {
          CameraManager.Instance.setOrientationWidgetVisible(false);
        }
      }
      break;
    }

    case 'displayGroup':
      VisibilityManager.Instance.setVisibility(body.group, body.visible);
      break;
  }
});

vscode.postMessage({ type: 'ready' });
