---
platform: linkedin
date: 2026-07-01
title: v1.10-v1.13 release recap
url:
media: media/2026-07-01-linkedin-v1-13-release.mp4
---

Something crossed a line with VS Code Aster this spring. 👀

When we first built it, the extension was a useful wrapper: open a .med mesh, edit your .export, hit run. Handy, but you still needed the code_aster documentation open in a browser tab to write anything serious.

With v1.10, that changed. ✨

🎨 The .comm editor got a full overhaul. Syntax highlighting was rewritten from scratch so commands, keywords, values, and nested _F(...) blocks all color correctly. Hover cards were redesigned in the style of a TypeScript IDE: signature first, then a description, the list of rules, and a link to the versioned documentation. Completions are now context-aware, filtering by what you've already typed and suggesting only variables whose type matches the expected keyword. And as you edit, the extension flags mistakes in real time: unknown command, missing required keyword, type mismatch, undefined variable, with one-click quick fixes. 🔧

🔗 All of this is version-aware. The extension reads its command catalog straight from your cave-selected Docker image, so everything above reflects the exact version of code_aster you're running. Switch version in the status bar and the editor updates automatically.

🗂️ A new activity-bar sidebar ties it all together. It shows your setup status at a glance, surfaces quick actions filtered to whatever file is active, and includes a full command browser: five canonical families (Mesh / Material / BC & Loads / Analysis / Output), each listing the commands already used in your file first so the most relevant ones are always at the top. A title-bar action opens a Cmd+P-style QuickPick over the entire catalog. Version management and links to external resources are there too.

🛠️ The setup experience got the same attention. The first time you open a .comm file, a guided flow walks you through Python deps, ruff, Docker, cave, and your code_aster image step by step, opt-in at every stage.

If that's the foundation, here's what we built on top of it:

🔍 Generate study from scenario (beta, v1.12): pick a mesh and a scenario (linear static, nonlinear static, modal), fill in a guided form, and get a ready-to-run .comm + .export with real group names pulled from the mesh. A working study in minutes, not hours.

✅ Validate Current Study (v1.13): before you even hit Run, a single command checks your .comm for command and concept consistency, and cross-references every file unit between the .comm and .export. Catches the mistakes that would only show up mid-run.

There's more too: searchable group lists and element/node counters in the mesh viewer 🔎, full WSL support for mixed Windows/Linux setups, and an automated test suite across the whole extension.

We're genuinely proud of how far this has come, and it keeps moving because of the feedback you send us. 🙏

👉 https://marketplace.visualstudio.com/items?itemName=simvia.vs-code-aster

#codeaster #VScodeaster #opensimulation #engineering #fem #python
