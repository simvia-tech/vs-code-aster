# Changelog

All notable changes to the **VS Code Aster** extension will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
