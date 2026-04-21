# Changelog

All notable changes to the **VS Code Aster** extension will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.9.0] - 2026-04-21

Volume and edge groups now appear in the viewer alongside face and node groups, a new "Groups" settings tab exposes per-kind display tweaks, the bundled vtk.js is replaced by the tree-shaken npm package, and an optional animated background adds a cosmetic touch.

### Added
- **Volume groups** — `med2obj.py` now computes the skin of every volume group in a 3D `.med` mesh and writes it into the `.obj` as a dedicated group. The viewer renders them as their own category with a filled isometric cube icon, toggle-able independently from face groups.
- **Edge groups** — level -2 groups (1D named cells) are extracted too and rendered as lines via a new `EdgeActorCreator`. Line width and depth offset (to avoid z-fighting with the skin) are user-controllable.
- **Groups settings tab** — new tab in the viewer Settings popup covering:
  - Edge-group thickness slider (1–10 px)
  - Edge-group depth-offset toggle
  - Node-group point-size multiplier (0.25×–4×)
  - Sidebar sort order (natural / by cell count)
  - Bucket groups by kind (on by default; off merges all four kinds into a single list sorted by the same order)
- **Group-kinds legend** in the help popup's Groups tab, showing each icon with a short description.
- **Edge threshold multiplier** is now persisted across sessions via `vs-code-aster.viewer.edgeThresholdMultiplier` (was previously editable but lost on reopen).
- **Dream background** — optional cosmetic viewer setting (`vs-code-aster.viewer.dreamBackground`) that drifts four EDF orange/blue blobs behind the mesh via a WebGL fragment shader. Theme-aware: blob intensity adapts to light vs dark themes, peak intensity is capped so overlapping blobs never fully replace the theme color. Does not affect mesh lighting.

### Changed
- **vtk.js migrated to `@kitware/vtk.js` npm package** — the 2.6 MB bundled script is gone, replaced by tree-shaken ES-module imports and real TypeScript types. Opens the door to regular version upgrades.
- **Settings popup**: the "Edges" tab is renamed to "Mesh edges" and its copy rewritten to distinguish the wireframe edges drawn on each cell from the new edge groups. Tab content now scrolls when it overflows instead of clipping.
- **Sidebar groups** now bucket volumes, faces, edges, and nodes in that order, each with its own icon.

### Fixed
- Mesh edge colors now repaint immediately on theme switch instead of waiting for the next camera move.
- Translucent meshes (highlighted parent behind a selected sub-group) no longer wash out on light themes — vtk.js 35's Order-Independent Transparency pass is bypassed in favor of plain SRC_ALPHA blending.
- `.obj` files cached under `.vs-code-aster/mesh_cache/` from older extension versions are invalidated when the converter changes (via the bumped `med2obj-version: 2` header).
- **Screenshots** now work again after the vtk.js migration — the capture path switched to vtk.js's `captureNextImage` API (which doesn't depend on `preserveDrawingBuffer`), and the dream background is composited behind the mesh when enabled. The screenshot button's hover highlight is also stripped from the full-viewer capture so it no longer bakes into the saved image.

## [1.8.1] - 2026-04-20

Follow-up polish on the `.export` editor form: smarter autocomplete suggestions and the saved file now opens automatically after create/save.

### Added
- **Type-aware autocomplete** — file name suggestions in the export form are now filtered by the selected F-line type so irrelevant files are hidden:
  - `mmed` / `rmed` rows accept `.med`, `.mmed`, `.rmed`, and any custom extension registered in `vs-code-aster.medFileExtensions` (so user-added MED extensions like `.71` show up).
  - `comm` rows accept `.com*` (covers `.comm`, `.com0`, `.com1`, ...).
  - `mess`, `msh`, and `dat` rows require a literal extension match.
  - Types without a conventional extension (`mail`, `base`, `libr`, `tab`, `nom`) still accept any file.
- **Autocomplete on output rows** — output file name fields now use the same autocomplete dropdown as inputs, making it easy to reuse existing file names for outputs.
- **Reveal on save** — creating or saving an `.export` file from the form now opens the file in a text editor (or focuses the existing tab if it's already open), so you immediately see the formatted result. Stale tabs left over from a rename are closed automatically.

### Fixed
- The hidden `.vs-code-aster/` folder no longer appears in the export form's autocomplete suggestions.

## [1.8.0] - 2026-04-20

Full rewrite of the `.export` form in Svelte + Tailwind, first-class language support for `.export` files (syntax highlighting, formatter, format-on-save), and a batch of UX upgrades.

### Added
- **Redesigned export form** — rewritten in Svelte 5 + Tailwind 4, styled with VS Code theme tokens (`--vscode-input-*`, `--vscode-focusBorder`, `--vscode-editorWarning-foreground`, ...), so it looks native in every theme.
  - Tab icon is a blue pencil; tab title lives-updates to match the filename (falls back to `untitled`).
  - Titles inside the form adapt to mode: "Create a new export file" vs "Edit an export file".
  - New export files are pre-seeded with a sensible default: `comm` + `mmed` inputs and an `rmed` output, filenames `simvia.comm / simvia.mmed / simvia.rmed`.
  - `.export` extension locked as a visual suffix on the filename field — it can't be edited away.
  - Nested paths supported in the filename (`subdir/file.export`); missing folders are created on save.
  - Unsaved drafts persist via `vscode.setState` + `retainContextWhenHidden`, so switching tabs or reloading the panel no longer clears the form.
- **File rows** — drag-to-reorder (powered by [`svelte-dnd-action`](https://github.com/isaacHagoel/svelte-dnd-action), theme-colored drop zones, keyboard-accessible); per-row × delete; full-width "Add input/output file" button at the end of each section.
  - Type dropdown is filtered by direction (inputs vs outputs) and shows a `Type` placeholder on new rows; the file-type list is the full code_aster set (`comm, mmed, rmed, mess, nom, base, mail, libr, tab, msh, dat`).
  - Unit auto-increment scoped to the same type and max+1 (so `med: 20, 50` → next is `51`, not `21`), idempotent when re-picking the same type; `nom` rows are locked to unit 0; ArrowUp/Down steps integer inputs.
  - Name autocomplete list matches the type dropdown styling; empty rows (no type and no name) are ignored by validation and on save.
- **Validation** — per-field inline error messages, a sticky footer with clickable error / warning counts that smooth-scroll to the corresponding panel.
  - Blocking errors: filename required, parameters must be integers, at least one `comm` input file required.
  - Non-blocking warnings: duplicate unit across files (listing the file names), no mesh file set, no `rmed` output set, rename-in-edit-mode (tells the user the original file will be deleted).
- **`.export` language support** — new TextMate grammar (`source.export`) colors `P`/`F` directives, parameter names, file types, direction flags (`D` vs `R`/`RC`), unit numbers, and `#` comments.
- **Document formatter for `.export`** — available via Format Document. On save/create the form applies the same formatter automatically:
  - Groups lines into `# Simulation parameters`, `# Input files`, `# Output files` sections separated by blank lines.
  - Sorts F lines within each direction by a canonical type priority (`comm, mmed, rmed, mess, nom, base, mail, libr, tab, msh, dat`).
  - Keeps standalone `#` comments attached to the line they precede.
  - Emits a three-line header at the top crediting VS Code Aster and Simvia; re-saving is idempotent (no stacked headers).
- Dedicated pencil icon (`media/images/icone-edit.svg`) for the "Edit export file" command, replacing the plain `$(book)` codicon.
- Extension now activates on `onLanguage:export`, so opening a `.export` file registers the formatter without any prior command run.
- Refreshed Simvia logo (new SVG), separate light/dark variants for both Simvia and code_aster logos in the form header.

### Changed
- Editing a file and changing its name now _renames_ the file on disk (old file is deleted after the new one is written). A warning panel previews the rename before the user saves.
- When writing a file, the output is always formatted (P/F grouping, section headers, shoutout) — so files stay clean across multiple save cycles.

### Fixed
- Loading an existing `.export` into the form (e.g. after a tab switch) no longer clobbers the pre-filled data with the seeded default.
- Removing the last row no longer leaves stale autocomplete suggestions keyed to the dead row.
- Missing parent directories no longer cause save to fail silently when the filename contains a path separator.

### Removed
- The legacy vanilla HTML/CSS/JS export form (`webviews/export/export.{html,css,js}`) and its hardcoded blue-on-light styling.
- Unused media assets: `media/images/aster.png`, `media/icons/3d.svg`, `media/icons/3d_light.svg`.

## [1.7.1] - 2026-04-17

Centralize extension-generated files under a single `.vs-code-aster/` folder per project, with timestamped run logs and automatic migration from legacy locations.

### Added
- Project-local `.vs-code-aster/` folder grouping all extension-generated files:
  - `mesh_cache/` — converted `.obj` files (previously `.visu_data/`)
  - `screenshots/` — PNGs saved from the viewer's screenshot button (previously next to source files)
  - `run_logs/` — one timestamped log per code_aster run (previously a single overwritten `.vscode-aster-run.log`)
- New `vs-code-aster.maxRunLogs` setting (default `10`) to cap run-log retention; oldest logs are pruned when a new run starts
- `med2obj-version` header in generated `.obj` files: the extension now detects stale caches from older converter versions and regenerates them automatically
- Automatic migration of legacy `.visu_data/` and `.vscode-aster-run.log` on first use, with info notifications so users know where files moved

## [1.7.0] - 2026-04-16

New viewer toolbar with bounding box, wireframe, and screenshot tools.

### Added
- Top toolbar in the mesh viewer with three new tools:
  - **Bounding box**: toggleable wireframe cube with colored axes (X red, Y green, Z blue), corner dots, a "0" origin marker, and dimension labels anchored in 3D
  - **Wireframe mode**: toggle between solid surface and wireframe rendering to inspect mesh density
  - **Screenshot**: left click saves the 3D view as PNG next to the source file and copies to clipboard; right click captures the full viewer including the sidebar
- Toolbar button tooltips using the same inline hover pattern as the rest of the UI
- Toolbar tab in the viewer help popup documenting the three new tools
- Updated README with diagnostics, terminal reuse, direct `.med` opening, and toolbar features

### Fixed
- Popup z-order: help and settings popups no longer render behind the sidebar
- Sidebar tooltip z-order: filter/clear tooltips no longer hidden behind the top toolbar

## [1.6.1] - 2026-04-15

Standalone mesh visualization: click any `.med` file to open the viewer directly, even without a `.comm`/`.export` pair.

### Added
- Click a `.med` / `.mmed` / `.rmed` file in the explorer to open it straight in the mesh viewer, via a custom editor registered with `priority: "default"` that bypasses the "file is binary" warning
- Automatic MED detection: when a tab opens a file whose first bytes match the HDF5 signature, a notification offers to register the extension (e.g. `.71`) and open it in the viewer in one click
- "Open as MED mesh" action exposed as an editor-title button (on auto-detected MED files) and as a right-click entry in the explorer
- Tabs for files whose extensions are in `vs-code-aster.medFileExtensions` are auto-rerouted to the mesh viewer, no window reload required after registering a new extension
- The mesh viewer tab now carries the shared orange cube icon (same as `.med` files in the file tree)
- Inline error state in the viewer: when `.med`→`.obj` conversion fails (e.g. `medcoupling` not installed), the reason is shown in the tab instead of an indefinite loading screen

## [1.6.0] - 2026-04-15

Run workflow overhaul: terminal reuse, automatic diagnostics in the Problems panel, and refreshed toolbar icons.

### Added
- Run diagnostics: `<A>` warnings and `<E>`/`<F>` errors from code_aster, Python tracebacks, `SyntaxError`s, fatal errors (e.g. segfaults), and MED/Fortran errors now surface automatically in the VS Code Problems panel — no `F mess` entry required in the `.export`
- Diagnostics attached to the originating `.comm`/`.com1` line when possible (via CMDTAG markers and Python tracebacks), and cleared between runs
- The existing `code-aster runner` terminal is now reused across runs instead of spawning a new one each time
- Colored toolbar icons: blue rocket for the run button (shared with the `.export` file icon) and orange eye for the mesh viewer button (matches the `.med` palette)

## [1.5.4] - 2026-04-15

File icon improvements and language support for `.export` and MED files.

### Added
- Dedicated file icons for `.export` files (blue rocket) and `.med` / `.mmed` / `.rmed` files (orange cube)
- Refreshed code_aster logo, now bundled with its SVG source
- `vs-code-aster.medFileExtensions` setting to register arbitrary extensions (e.g. `.21`, `.71`) as MED files, which code_aster writes under the I/O unit number

## [1.5.3] - 2026-03-26

Comment toggle support and Windows debugging improvements.

### Added
- Language configuration and keybindings for toggling line comments in `.comm` files
- Support for attaching to code_aster embedded Python on Windows installations

## [1.5.2] - 2026-03-23

Various fixes and improvements.

### Added
- Export form now auto-increments unit numbers to avoid duplicates when adding new files
- Files named `export` (without extension) are now detected as export files

### Fixed
- Mesh viewer now correctly resolves .med file paths containing subdirectories (e.g. `Mesh/mesh.med`) relative to the .export file location ([#13](https://github.com/simvia-tech/vs-code-aster/issues/13))
- Selecting text no longer resets manually hidden objects in the mesh viewer ([#14](https://github.com/simvia-tech/vs-code-aster/issues/14))
- Fixed issues when two meshes share groups with the same name ([#15](https://github.com/simvia-tech/vs-code-aster/issues/15))
- Fixed error in mesh viewer ([#16](https://github.com/simvia-tech/vs-code-aster/issues/16))
- Reduced extension package size by excluding unnecessary files

## [1.5.1] - 2026-03-16

Various fixes and optimizations.

### Added
- Selecting object names in text editors hides all other objects (hence highlighting selected object)
- Progress bar for mesh loading

### Fixed
- Text selection now highlights groups again
- Group sorting order now handles alphanumerical sorting

## [1.5.0] - 2026-03-13

Rewrote the mesh viewer UI with Svelte, and added new viewer features.

### Added
- Migrated the mesh viewer frontend from vanilla JS/HTML to Svelte with TypeScript
- Mesh viewer UI now follows the VS Code user theme
- Object file names are shown in the webview tab titles
- Focusing a `.comm` file now focuses its corresponding mesh viewer webview
- Revamped help popup with tabs and more tips
- New settings popup with various settings
    - Edge rendering settings
    - Object visibility settings
    - UI settings
- Improved various UI components in the mesh viewer
- Show/hide toggle button per object in the sidebar
- Per-object color display
- Zoom widget in the mesh viewer

## [1.4.3] - 2026-03-03

Updated dependencies.

### Added
- More recent versions for a lot of dependencies

### Removed
- Unused packages

## [1.4.2] - 2026-03-03

Fixed issues when different objects have groups with the same name.

### Fixed
- Clicking on a group who has a name shared with other groups will now properly highlight the correct group.

## [1.4.1] - 2026-03-03

Improved med file detection.

### Fixed
- Med files that do not have a .*med extension are now properly detected as med files for the med viewer.

## [1.4.0] - 2026-02-04

Added support for more comm file extensions

### Added
- .com, .com[0-9] file extensions are now supported.

### Fixed
- [It can only read .comm files #7](https://github.com/simvia-tech/vs-code-aster/issues/7)

## [1.2.0] - 2026-01-21

Added support for 2D meshes in the visualizer

### Added
- 2D meshes are now supported by the visualizer.

### Fixed
- [Mesh viewer fail on astest SSLP106a #4](https://github.com/simvia-tech/vs-code-aster/issues/4)

## [1.1.0] - 2026-01-08

Added support for quadratic nodes in the visualizer

### Added
- Quadratic nodes are now correctly displayed in the visualization

### Fixed
- [Wrong numbering for the mesh viewer #1](https://github.com/simvia-tech/vs-code-aster/issues/1)

## [1.0.2] - 2026-01-07

Micro-patch to fix Python < 3.10 issues.

### Fixed
- Removed modern typing and use legacy one to be compatible with older Python version. Python 3.8 or later is still required.

## [1.0.1] - 2025-12-18

Micro-patch to fix README issues.

### Fixed
- **Simvia logo** in the README now uses an absolute link rather than a relative link

## [1.0.0] - 2025-12-17

Initial public release — first stable feature set.

### Added

- **Interactive export form:** Create and edit `.export` files from VS Code (command palette entry and editor button) with validation and a single-click create flow.
- **Run simulations:** Launch simulations from a `.export` file (uses `cave run [file].export` by default); run command is configurable via the extension settings.
- **Smart `.comm` editing:** Syntax highlighting, hover documentation (command descriptions, arguments, types, defaults), signature help, contextual auto-completion, and a status bar showing step progress with a detailed view.
- **Integrated 3D visualizer:** VTK.js-based viewer to load `.med` meshes, highlight face/node groups, interact with camera (rotate/pan/zoom), quick axis alignment, and mesh conversion to `.obj` stored in a hidden `.visu_data/` folder.
- **Documentation and requirements:** Installation notes for Python 3.8+, `numpy`, `pygls==1.3.1`, and `medcoupling`, plus instructions for optional `cave` installation.
- **Troubleshooting:** Ability to restart the language server for `.comm` files to restore hover/signature/completion features.
