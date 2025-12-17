# 🧭 Product Roadmap — VS Code Aster

> Make **code_aster** input file writing faster, safer, and more accessible directly from VS Code.

The extension aims to reduce friction between modeling, validation, execution, and analysis by bringing **code_aster** native workflows into the editor.

## Current Capabilities (v1.0.0)

- `.export` file generator
- 3D mesh viewer
- **code_aster** command language auto-completion with inline help (VS Code tooltips)
- **code_aster** execution from VS Code

## Roadmap

### Short Term — stability & reliability

**Goal** : *Harden existing features for daily production use.*
- Harden the Language Server
    - Improved parsing robustness
    - Better error recovery
    - Performance and memory optimizations
- Harden the `.export` file generator
    - Validation of generated files
    - Better error reporting
    - Support for common real-world configurations
- Improve **code_aster** execution integration
    - Clearer execution status and feedback
    - Better handling of runtime failures

### Mid Term —  experience & feedback

**Goal** : *Improve user feedback and guidance inside VS Code.*
- Open **code_aster** documentation directly from VS Code
    - Command-level documentation lookup
    - Context-aware links from auto-completion or diagnostics
- Parse **code_aster** log files
    - Detect WARNING, ALARM, and ERROR
    - Surface issues in the VS Code Problems panel
    - Clickable navigation from diagnostics to source lines
- Improve error messaging and diagnostics consistency across the extension

### Long Term — intelligence & domain knowledge

**Goal** : *Move from syntax assistance to domain-aware guidance*.
- Enrich auto-completion with context and domain logic
    - Context-aware suggestions based on :
        - Command position
        - Previously defined concepts
        - Analysis type (static, modal, nonlinear, etc.)
    - Detection of incompatible or suspicious command combinations
    - Early feedback before execution
- Progressive validation of input files
    - From syntactic → semantic → domain-level checks

## Out of Scope (for now)

- Full solver debugging
- Automatic model correction
- Non–code_aster solvers
- Results visualization

## Success Criteria

- Reduction of input-file related runtime errors
- Faster model setup for new users
- Increased adoption in real production workflows
- Positive feedback from experienced **code_aster** users

## Open-Source Principles

- Transparent roadmap and changelog
- Semantic versioning
- Backward compatibility when possible
- Community-driven improvements