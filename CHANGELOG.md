# Changelog

All notable changes to the **VS Code Aster** extension will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-12-17

Initial public release — first stable feature set.

### Added

- **Interactive export form:** Create and edit `.export` files from VS Code (command palette entry and editor button) with validation and a single-click create flow.
- **Run simulations:** Launch simulations from a `.export` file (uses `cave run [file].export` by default); run command is configurable via the extension settings.
- **Smart `.comm` editing:** Syntax highlighting, hover documentation (command descriptions, arguments, types, defaults), signature help, contextual auto-completion, and a status bar showing step progress with a detailed view.
- **Integrated 3D visualizer:** VTK.js-based viewer to load `.med` meshes, highlight face/node groups, interact with camera (rotate/pan/zoom), quick axis alignment, and mesh conversion to `.obj` stored in a hidden `.visu_data/` folder.
- **Documentation and requirements:** Installation notes for Python 3.8+, `numpy`, `pygls==1.3.1`, and `medcoupling`, plus instructions for optional `cave` installation.
- **Troubleshooting:** Ability to restart the language server for `.comm` files to restore hover/signature/completion features.
