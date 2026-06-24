<script lang="ts">
  import { onMount } from 'svelte';
  import type { Modelization, Scenario, LoadType } from '@scenario/spec';
  import { generateComm } from '@scenario/generateComm';
  import { generateExport } from '@scenario/generateExport';
  import {
    SCENARIOS,
    MODELIZATIONS,
    LOAD_TYPES,
    MATERIAL_PRESETS,
    availableDofs,
    materialKinds,
    loadGroupKinds,
  } from '@scenario/studyMeta';
  import {
    type Draft,
    type MeshGroups,
    type TaggedGroup,
    FIELD,
    defaultDraft,
    draftToSpec,
    validateDraft,
    taggedGroups,
  } from '../lib/draft';
  import Header from '../../../shared/components/Header.svelte';
  import SubmitBar from '../../../shared/components/SubmitBar.svelte';
  import Dropdown from '../../../shared/components/ui/Dropdown.svelte';
  import Checkbox from '../../../shared/components/ui/Checkbox.svelte';
  import GroupMultiSelect from './GroupMultiSelect.svelte';
  import PreviewPane from './PreviewPane.svelte';

  interface VsCodeApi {
    postMessage(msg: unknown): void;
    getState(): unknown;
    setState(state: unknown): void;
  }

  let vscode: VsCodeApi | undefined;
  try {
    vscode = (window as unknown as { acquireVsCodeApi: () => VsCodeApi }).acquireVsCodeApi();
  } catch (e) {
    console.error('acquireVsCodeApi failed', e);
  }

  const EMPTY_GROUPS: MeshGroups = { volumes: [], surfaces: [], edges: [], nodes: [] };

  const saved = (vscode?.getState() as { draft?: Draft } | undefined) ?? undefined;
  let draft = $state<Draft>(saved?.draft ?? defaultDraft());
  let meshGroups = $state<MeshGroups>(EMPTY_GROUPS);
  let groupsAvailable = $state(true);
  let initialized = $state(false);

  let simviaLogoUrl = $state('');
  let simviaLogoDarkUrl = $state('');
  let asterLogoUrl = $state('');
  let asterLogoDarkUrl = $state('');

  const isStructural = $derived(draft.modelization === 'DKT' || draft.modelization === 'POU_D_T');
  const spec = $derived(draftToSpec(draft));
  const errors = $derived(validateDraft(draft));

  // Which preset (if any) the current E/NU/RHO match — drives the preset
  // dropdown label and auto-reverts to "Custom" once the user edits a value.
  const presetValue = $derived(
    MATERIAL_PRESETS.find(
      (p) =>
        String(p.young) === draft.young.trim() &&
        String(p.poisson) === draft.poisson.trim() &&
        String(p.rho) === draft.rho.trim()
    )?.label ?? ''
  );

  function safe(fn: () => string): string {
    try {
      return fn();
    } catch (e) {
      return `# preview unavailable: ${(e as Error).message}`;
    }
  }
  const commPreview = $derived(safe(() => generateComm(spec)));
  const exportPreview = $derived(safe(() => generateExport(spec)));

  // Prefer the modelization-appropriate element groups; if the mesh has none of
  // that kind, fall back to all element groups so the dropdown still appears
  // (rather than silently dropping to a free-text field).
  const materialStrict = $derived(taggedGroups(meshGroups, materialKinds(draft.modelization)));
  const materialCandidates = $derived(
    materialStrict.length > 0
      ? materialStrict
      : taggedGroups(meshGroups, ['volume', 'surface', 'edge'])
  );
  const structuralCandidates = $derived(
    taggedGroups(meshGroups, draft.modelization === 'DKT' ? ['surface'] : ['edge'])
  );
  const bcCandidates = $derived(taggedGroups(meshGroups, ['surface', 'edge', 'node']));
  const loadCandidates = $derived(taggedGroups(meshGroups, loadGroupKinds(draft.loadType)));
  const dofChoices = $derived(availableDofs(draft.modelization));

  const meshGroupCount = $derived(
    meshGroups.volumes.length +
      meshGroups.surfaces.length +
      meshGroups.edges.length +
      meshGroups.nodes.length
  );

  function pruneSelectionsToMesh() {
    const all = new Set([
      ...meshGroups.volumes,
      ...meshGroups.surfaces,
      ...meshGroups.edges,
      ...meshGroups.nodes,
    ]);
    const keep = (gs: TaggedGroup[]) => gs.filter((g) => all.has(g.name));
    draft.materialGroups = keep(draft.materialGroups);
    draft.structuralGroups = keep(draft.structuralGroups);
    draft.bcGroups = keep(draft.bcGroups);
    draft.loadGroups = keep(draft.loadGroups);
  }

  interface InitMessage {
    command: string;
    groups?: MeshGroups;
    groupsAvailable?: boolean;
    meshFileName?: string;
    simviaLogoUrl?: string;
    simviaLogoDarkUrl?: string;
    asterLogoUrl?: string;
    asterLogoDarkUrl?: string;
  }

  function handleMessage(msg: InitMessage) {
    if (msg.command === 'init' || msg.command === 'meshChanged') {
      meshGroups = msg.groups ?? EMPTY_GROUPS;
      groupsAvailable = msg.groupsAvailable ?? false;
      if (msg.meshFileName) {
        draft.meshFileName = msg.meshFileName;
      }
      if (msg.command === 'init') {
        simviaLogoUrl = msg.simviaLogoUrl ?? '';
        simviaLogoDarkUrl = msg.simviaLogoDarkUrl ?? '';
        asterLogoUrl = msg.asterLogoUrl ?? '';
        asterLogoDarkUrl = msg.asterLogoDarkUrl ?? '';
      }
      if (groupsAvailable) {
        pruneSelectionsToMesh();
      }
      initialized = true;
    }
  }

  onMount(() => {
    const handler = (e: MessageEvent) => handleMessage(e.data);
    window.addEventListener('message', handler);
    vscode?.postMessage({ command: 'ready' });
    return () => window.removeEventListener('message', handler);
  });

  // Persist the draft + keep the panel title in sync with the study name.
  $effect(() => {
    vscode?.setState({ draft: $state.snapshot(draft) });
  });
  $effect(() => {
    vscode?.postMessage({ command: 'titleChange', name: draft.baseName.trim() });
  });

  function setModelization(m: Modelization) {
    draft.modelization = m;
    draft.bcDofs = availableDofs(m);
    draft.structuralGroups = [];
  }

  function applyPreset(label: string) {
    const preset = MATERIAL_PRESETS.find((p) => p.label === label);
    if (!preset) {
      return;
    }
    draft.young = String(preset.young);
    draft.poisson = String(preset.poisson);
    draft.rho = String(preset.rho);
  }

  function toggleDof(dof: string) {
    draft.bcDofs = draft.bcDofs.includes(dof)
      ? draft.bcDofs.filter((d) => d !== dof)
      : [...draft.bcDofs, dof];
  }

  function numClass(value: string): string {
    return value.trim() !== '' && !Number.isFinite(Number(value)) ? 'input-warning' : '';
  }

  function submit() {
    if (errors.length > 0) {
      return;
    }
    vscode?.postMessage({ command: 'submit', spec });
  }
  const cancel = () => vscode?.postMessage({ command: 'cancel' });
  const browseMesh = () => vscode?.postMessage({ command: 'browseMesh' });

  function focusTarget(id: string) {
    const el = document.getElementById(id);
    if (!el) {
      return;
    }
    el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    el.focus({ preventScroll: true });
    // Flash a highlight ring so the field is obvious even when it isn't
    // focusable (e.g. the group dropdowns). Restart on repeated clicks.
    el.classList.remove('field-flash');
    void el.offsetWidth;
    el.classList.add('field-flash');
  }

  const inputClass =
    'rounded border border-ui-input-border bg-ui-input-bg px-2 py-1 text-ui-input-fg';
</script>

<div class="flex h-screen flex-col" style="color: var(--ui-fg)">
  {#snippet trigger(label: string)}
    <button
      type="button"
      class="{inputClass} flex w-full cursor-pointer items-center justify-between gap-1"
    >
      <span class="truncate">{label}</span>
      <svg width="8" height="8" viewBox="0 0 8 8" fill="currentColor" aria-hidden="true">
        <path d="M1 2.5 L4 5.5 L7 2.5 Z" />
      </svg>
    </button>
  {/snippet}

  <div class="px-8 pt-4">
    <Header
      title="Generate study from scenario (beta)"
      compact
      {simviaLogoUrl}
      {simviaLogoDarkUrl}
      {asterLogoUrl}
      {asterLogoDarkUrl}
    />
  </div>

  <div class="flex min-h-0 flex-1">
    <!-- Form -->
    <section class="flex w-1/2 min-h-0 flex-col">
      <div class="flex flex-1 flex-col gap-4 overflow-auto px-8 pt-3 pb-4">
        {#if initialized && !groupsAvailable}
          <div
            class="rounded border px-3 py-2 text-xs"
            style="color: var(--vscode-editorWarning-foreground, #cca700); border-color: var(--vscode-editorWarning-foreground, #cca700); background: color-mix(in srgb, var(--vscode-editorWarning-foreground, #cca700) 12%, transparent)"
          >
            Couldn’t read the mesh groups (is <code>medcoupling</code> installed for the configured Python?).
            Type group names manually below, or pick another mesh.
          </div>
        {:else if initialized && meshGroupCount === 0}
          <div
            class="rounded border px-3 py-2 text-xs"
            style="color: var(--vscode-editorWarning-foreground, #cca700); border-color: var(--vscode-editorWarning-foreground, #cca700); background: color-mix(in srgb, var(--vscode-editorWarning-foreground, #cca700) 12%, transparent)"
          >
            This mesh has no named groups. Define groups in your mesh (GROUP_MA / GROUP_NO), pick
            another mesh, or type group names manually below.
          </div>
        {/if}
        <label class="flex flex-col gap-1">
          <span class="text-sm text-ui-text-secondary">Analysis scenario</span>
          <Dropdown
            options={SCENARIOS.map((s) => ({ value: s.value, label: s.label }))}
            value={draft.scenario}
            onSelect={(v) => (draft.scenario = v as Scenario)}
          >
            {@render trigger(SCENARIOS.find((s) => s.value === draft.scenario)?.label ?? '')}
          </Dropdown>
          <span class="text-xs text-ui-text-muted">
            {SCENARIOS.find((s) => s.value === draft.scenario)?.detail}
          </span>
        </label>

        <label class="flex flex-col gap-1">
          <span class="text-sm text-ui-text-secondary">Modelization</span>
          <Dropdown
            options={MODELIZATIONS.map((m) => ({
              value: m.value,
              label: `${m.label} — ${m.detail}`,
            }))}
            value={draft.modelization}
            onSelect={(v) => setModelization(v as Modelization)}
          >
            {@render trigger(
              MODELIZATIONS.find((m) => m.value === draft.modelization)?.label ?? ''
            )}
          </Dropdown>
        </label>

        <!-- Material -->
        <fieldset class="flex flex-col gap-2 rounded border border-ui-border p-3">
          <legend class="px-1 text-sm font-medium">Material</legend>
          <div class="flex flex-col gap-1">
            <span class="text-sm text-ui-text-secondary">Preset</span>
            <Dropdown
              options={MATERIAL_PRESETS.map((p) => ({ value: p.label, label: p.label }))}
              value={presetValue}
              onSelect={(v) => applyPreset(v)}
            >
              {@render trigger(presetValue || 'Custom')}
            </Dropdown>
          </div>
          <label class="flex items-center justify-between gap-2 text-sm">
            <span class="text-ui-text-secondary">Young’s modulus (E)</span>
            <input
              class="{inputClass} {numClass(draft.young)}"
              inputmode="decimal"
              id={FIELD.young}
              bind:value={draft.young}
            />
          </label>
          <label class="flex items-center justify-between gap-2 text-sm">
            <span class="text-ui-text-secondary">Poisson’s ratio (NU)</span>
            <input
              class="{inputClass} {numClass(draft.poisson)}"
              inputmode="decimal"
              id={FIELD.poisson}
              bind:value={draft.poisson}
            />
          </label>
          {#if draft.scenario === 'modal'}
            <label class="flex items-center justify-between gap-2 text-sm">
              <span class="text-ui-text-secondary">Density (RHO)</span>
              <input
                class="{inputClass} {numClass(draft.rho)}"
                inputmode="decimal"
                id={FIELD.rho}
                bind:value={draft.rho}
              />
            </label>
          {/if}
          {#if draft.scenario === 'nonlinear-static'}
            <label class="flex items-center justify-between gap-2 text-sm">
              <span class="text-ui-text-secondary">Yield stress (SY)</span>
              <input
                class="{inputClass} {numClass(draft.yieldStress)}"
                inputmode="decimal"
                id={FIELD.yield}
                bind:value={draft.yieldStress}
              />
            </label>
            <label class="flex items-center justify-between gap-2 text-sm">
              <span class="text-ui-text-secondary">Hardening (D_SIGM_EPSI)</span>
              <input
                class="{inputClass} {numClass(draft.hardening)}"
                inputmode="decimal"
                id={FIELD.hardening}
                bind:value={draft.hardening}
              />
            </label>
          {/if}
        </fieldset>

        <GroupMultiSelect
          label="Material assignment groups"
          candidates={materialCandidates}
          selected={draft.materialGroups}
          freeTextKind={materialKinds(draft.modelization)[0]}
          hint="Leave empty to assign to the whole mesh (TOUT='OUI')."
          onChange={(g) => (draft.materialGroups = g)}
        />

        {#if isStructural}
          <fieldset class="flex flex-col gap-2 rounded border border-ui-border p-3">
            <legend class="px-1 text-sm font-medium">
              {draft.modelization === 'DKT' ? 'Shell properties' : 'Beam properties'}
            </legend>
            <GroupMultiSelect
              label={draft.modelization === 'DKT' ? 'Shell groups' : 'Beam groups'}
              candidates={structuralCandidates}
              selected={draft.structuralGroups}
              id={FIELD.structuralGroups}
              freeTextKind={draft.modelization === 'DKT' ? 'surface' : 'edge'}
              required
              onChange={(g) => (draft.structuralGroups = g)}
            />
            {#if draft.modelization === 'DKT'}
              <label class="flex items-center justify-between gap-2 text-sm">
                <span class="text-ui-text-secondary">Thickness (EPAIS)</span>
                <input
                  class="{inputClass} {numClass(draft.shellThickness)}"
                  inputmode="decimal"
                  id={FIELD.thickness}
                  bind:value={draft.shellThickness}
                />
              </label>
            {:else}
              <label class="flex items-center justify-between gap-2 text-sm">
                <span class="text-ui-text-secondary">Section HY</span>
                <input
                  class="{inputClass} {numClass(draft.beamHy)}"
                  inputmode="decimal"
                  id={FIELD.beamHy}
                  bind:value={draft.beamHy}
                />
              </label>
              <label class="flex items-center justify-between gap-2 text-sm">
                <span class="text-ui-text-secondary">Section HZ</span>
                <input
                  class="{inputClass} {numClass(draft.beamHz)}"
                  inputmode="decimal"
                  id={FIELD.beamHz}
                  bind:value={draft.beamHz}
                />
              </label>
            {/if}
          </fieldset>
        {/if}

        <!-- Boundary conditions -->
        <fieldset class="flex flex-col gap-2 rounded border border-ui-border p-3">
          <legend class="px-1 text-sm font-medium">Boundary condition</legend>
          <GroupMultiSelect
            label="Constrained groups"
            candidates={bcCandidates}
            selected={draft.bcGroups}
            id={FIELD.bcGroups}
            freeTextKind="node"
            required
            onChange={(g) => (draft.bcGroups = g)}
          />
          <div class="flex flex-col gap-1">
            <span class="text-sm text-ui-text-secondary">Constrained DOFs (set to 0)</span>
            <div class="flex flex-wrap gap-2">
              {#each dofChoices as dof (dof)}
                <Checkbox
                  checked={draft.bcDofs.includes(dof)}
                  label={dof}
                  onchange={() => toggleDof(dof)}
                />
              {/each}
            </div>
          </div>
        </fieldset>

        <!-- Load -->
        {#if draft.scenario !== 'modal'}
          <fieldset class="flex flex-col gap-2 rounded border border-ui-border p-3">
            <legend class="px-1 text-sm font-medium">Load</legend>
            <div class="flex flex-col gap-1">
              <span class="text-sm text-ui-text-secondary">Type</span>
              <Dropdown
                options={LOAD_TYPES.map((t) => ({
                  value: t.value,
                  label: `${t.label} — ${t.detail}`,
                }))}
                value={draft.loadType}
                onSelect={(v) => (draft.loadType = v as LoadType)}
              >
                {@render trigger(LOAD_TYPES.find((t) => t.value === draft.loadType)?.label ?? '')}
              </Dropdown>
            </div>
            {#if draft.loadType !== 'PESANTEUR'}
              <GroupMultiSelect
                label="Loaded groups"
                candidates={loadCandidates}
                selected={draft.loadGroups}
                id={FIELD.loadGroups}
                freeTextKind={loadGroupKinds(draft.loadType)[0] ?? 'surface'}
                required
                onChange={(g) => (draft.loadGroups = g)}
              />
            {/if}
            <label class="flex items-center justify-between gap-2 text-sm">
              <span class="text-ui-text-secondary">
                {draft.loadType === 'PRES_REP'
                  ? 'Pressure (PRES)'
                  : draft.loadType === 'PESANTEUR'
                    ? 'Gravity (GRAVITE)'
                    : 'Force along Z (FZ)'}
              </span>
              <input
                class="{inputClass} {numClass(draft.loadValue)}"
                inputmode="decimal"
                id={FIELD.loadValue}
                bind:value={draft.loadValue}
              />
            </label>
          </fieldset>
        {/if}

        <!-- Modal -->
        {#if draft.scenario === 'modal'}
          <label class="flex items-center justify-between gap-2 text-sm">
            <span class="text-ui-text-secondary">Number of modes</span>
            <input
              class="{inputClass} {numClass(draft.nmodes)}"
              inputmode="numeric"
              id={FIELD.nmodes}
              bind:value={draft.nmodes}
            />
          </label>
        {/if}

        <!-- Output -->
        <fieldset class="flex flex-col gap-2 rounded border border-ui-border p-3">
          <legend class="px-1 text-sm font-medium">Output</legend>
          <label class="flex items-center justify-between gap-2 text-sm">
            <span class="text-ui-text-secondary">Study name</span>
            <input class={inputClass} id={FIELD.baseName} bind:value={draft.baseName} />
          </label>
          <div class="flex items-center justify-between gap-2 text-sm">
            <span class="text-ui-text-secondary">Mesh</span>
            <span class="flex items-center gap-2">
              <span class="font-mono text-xs">{draft.meshFileName || '(none)'}</span>
              <button
                type="button"
                class="cursor-pointer rounded px-2 py-0.5 text-ui-link underline hover:bg-ui-elem-hover hover:no-underline"
                onclick={browseMesh}>Browse…</button
              >
            </span>
          </div>
        </fieldset>
      </div>
      {#if errors.length > 0}
        <div
          class="shrink-0 border-t border-ui-border px-8 py-2 text-xs"
          style="color: var(--vscode-errorForeground, #d45858)"
        >
          {#each errors as e (e.id + e.message)}
            <button
              type="button"
              class="block cursor-pointer text-left hover:underline"
              onclick={() => focusTarget(e.id)}
            >
              • {e.message}
            </button>
          {/each}
        </div>
      {/if}
      <SubmitBar
        sticky={false}
        canSubmit={errors.length === 0}
        submitLabel="Generate study"
        errorCount={errors.length}
        onSubmit={submit}
        onCancel={cancel}
        onScrollToErrors={() => errors[0] && focusTarget(errors[0].id)}
      />
    </section>

    <!-- Preview -->
    <section class="flex w-1/2 min-h-0 flex-col border-l border-ui-border">
      <div class="flex shrink-0 items-baseline gap-2 px-3 pt-3 pb-1">
        <span class="text-sm font-medium text-ui-text-secondary">Preview</span>
        <span class="text-xs text-ui-text-muted">read-only — generated from your selections</span>
      </div>
      <div class="min-h-0 flex-1">
        <PreviewPane comm={commPreview} exportText={exportPreview} baseName={spec.baseName} />
      </div>
    </section>
  </div>
</div>
