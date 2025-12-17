<p align="center"><img src="./resources/images/simvia.png" alt="Simvia Logo" width="50%" /></p>

<p align="center">
  <a href="/"><img src="https://img.shields.io/badge/version-1.0.0-blue" alt="Version" /></a>
  <a href="./LICENSE"><img src="https://img.shields.io/badge/license-GPL%203.0-green" alt="License" /></a>
</p>

# VS Code Aster – VS Code Extension for code_aster

This is the first release of the **VS Code Aster** extension. The main objective is to collect feedback on any bugs or anomalies you encounter during its usage. All input regarding features is valuable, whether it's about how commands are triggered, unexpected behaviors, or options that could be added. Your experience and suggestions greatly help improve the extension.

## Description

**VS Code Aster** is a Visual Studio Code extension designed to simplify and speed up work with **code_aster**.
It offers:

- An interactive form to create or edit a `.export` file
- The ability to launch simulations directly from VS Code
- Advanced features for editing `.comm` files
- A fully integrated 3D Visualizer to explore your meshs

## Installation

### 1. Installing the extension

#### From the market place

The **VS Code Aster** extension is now available on the [VS Code Marketplace](https://marketplace.visualstudio.com/) :

1. Open VS Code then go to the Extensions tab (or press `Ctrl + Shift + X` / `Cmd + Shift + X`).
2. Search for `VS Code Aster`.
3. Click on **Install**.

#### From a .vsix file

- Download the .vsix file from the [latest release](https://github.com/simvia-tech/vs-code-aster/releases) :

  1. Choose your preferred version (latest is recommended)
  2. In the "Assets" section, click on the `vs-code-aster-[version].vsix` button.

> WSL users will need to copy the .vsix file to the WSL file system before continuing with the installation.
>
> ```
> cp /mnt/c/Users/[UserName]/Downloads/vs-code-aster-[version].vsix ~/
> ```

- Once you've got the `.vsix` file ready, you can open VS Code and :
  1. Open the Command Palette (`Ctrl + Shift + P` / `Cmd + Shift + P`).
  2. Search for and run `Extensions: Install from VSIX...`.
  3. Select the downloaded `.vsix` file.
  4. Reload your VS Code window — your extension is now installed !

### 2. Required dependencies

This extension requires **Python 3.8 or later** and the following packages :

- `numpy`
- `pygls==1.3.1`
- `medcoupling`

Here are **two ways** to install these packages :

#### 2.1. Use a dedicated Python virtual environment (recommended)

If you prefer to isolate your dependencies, or if pip cannot install system-wide packages, you can setup a virtual environment :

```bash
# Create a virtual environment
python3 -m venv ~/[env_name]

# Activate the venv
source ~/[env_name]/bin/activate

# Install required packages
pip install numpy pygls==1.3.1 medcoupling
```

Then point the extension to this environment :

1. Open `File > Preferences > Settings` (or press `Ctrl + ,` / `Cmd + ,`).
2. In the search bar, type `VS Code Aster`.
3. Locate `Python Executable Path`.
4. Set it to the absolute path of your environment’s Python executable, for example :

```
/home/[username]/[env_name]/bin/python
```

5. Reload the VS Code window (`Ctrl + R` / `Cmd + R`).

#### 2.2. Install directly with pip

If you'd rather install the Python packages globally :

```bash
pip install numpy pygls==1.3.1 medcoupling
```

### 3. (Optional) Installing Cave

If you'd like to run simulations, you need to have **cave** installed on your system. You can follow the instructions on [the cave GitHub repository](https://github.com/simvia-tech/cave).

You're now ready to use **VS Code Aster** !

## Usage / Features

## Features overview

### 1. Creating and managing .export files

The extension provides an interface to create and manage `.export` files more easily, through a web form.

#### Opening the form

There are two ways to open the form :

- Option 1 - recommended when creating a new file :
  - Open the Command Palette (`Ctrl + Shift + P` / `Cmd + Shift + P`)
  - Search for `Edit export file` then click on it.
  - The form will be pre-filled with placeholder data that should be modified to your desires.
- Option 2 - recommended when editing an existing file :
  1. Open an `.export` file.
  2. Click the book icon `Edit export file` in the top-right corner of the file.
  3. The form will be pre-filled with existing data, ready to be modified.

#### Key points

- Any field highlighted in red will block the creation of the export file.
- Once the `Create` button is clicked and the form is valid, a `.export` file will be created at the place it has been opened (replacing the previous file if it existed).

### 2. Launching a simulation

> You need to have **cave** installed on your system to launch simulations. Refer to [the cave GitHub repository](https://github.com/simvia-tech/cave) if you want to install **cave**.

**From a .export file**

1. Open a `.export` file.
2. Click on the "play" icon `Run with code_aster` in the top-right corner of the file.

It will open a terminal and execute the following command : `cave run [file].export`.

**Personnalize alias to run code-aster**

If you want to use a custom alias, you can :

1. Open VS Code.
2. Go to `File > Preferences > Settings` (or press `Ctrl + ,` / `Cmd + ,`).
3. In the search bar, type `VS Code Aster`.
4. Find the setting `Alias For Run` and change the value to the command you want to use to run **code_aster**.

### 3. Smart editing of .comm files

**Syntax highlighting**

- Dedicated highlighting for **code_aster** syntax, making `.comm` files more readable
- For the best experience, use a theme that differentiates functions, variables, etc.

**Hover documentation**

- When hovering over a **code_aster** command, a tooltip displays :
  - The command description
  - The command arguments
  - The types and default values of arguments

**Command signatures**

- When typing a `(` after a command name, or a `,` after entering an argument (e.g., `FORMAT="MED",`), a signature is displayed
- This signature shows the parameters (depending on context — some parameters are only available under certain conditions)

**Contextual auto-completion**

- The extension automatically suggests :
  - Command names
  - Relevant arguments depending on the current command

**Status Bar**

- A status bar is displayed at the bottom of the window, showing the number of steps completed in the current command file, e.g., `code_aster: 3/5 steps`.
- Clicking on the status bar opens a detailed view of completed commands for each family.

### 4. The visualizer — Interactive 3D result viewer

The visualizer is an integrated 3D viewer that lets you display and explore your simulation geometry and results directly in VS Code — without leaving your workspace.

It’s powered by **VTK.js**, and supports both mesh visualization and node-based groups.

#### Opening the visualizer

The visualizer is very easy to open :

1. Open a `.comm` file.
2. Click on the "eye" icon `Open visualizer` in the top-right corner of the file.

The visualizer is now open !

#### Features

- Load geometry files (`.med`) directly into the viewer
- Highlight face and node groups using the sidebar
- Highlight groups quickly by selecting their names from your command file (`.comm`)
- Control the camera with by rotating or panning it

#### Usage tips

- Group highlighting :
  - Click on a group name in the sidebar to highlight or unhighlight it
  - Click on the "clear" button in the sidebar to reset highlight status for all groups
  - Click on the "filter" button in the sidebar to choose which groups are easily accessible in the sidebar
  - Objects becomes transparent when you highlight their groups, helping visualize details more clearly
- Camera control :
  - Hold `Left click` and move your mouse to rotate the camera
  - Hold `Ctrl` + `Left click` and move your mouse to rotate the camera around an axis
  - Hold `Shift` + `Left click` and move your mouse to pan the camera
  - Use the `Mouse wheel` to zoom in and out
  - Click on the `X`, `Y`, and `Z` buttons at the bottom of the sidebar to quickly align the camera along an axis
- File management :
  - Mesh files (`.*med` files) are converted to `.obj` files, which are stored in a hidden folder called `.visu_data/` in your workspace

## Troubleshooting

If you encounter an error that seems to have broken the language server (for `.comm` files), you can restart it without closing VS Code:

1. Open the Command Palette (`Ctrl + Shift + P` / `Cmd + Shift + P`).
2. Type `Restart the LSP Server for code_aster` and select it.
3. The language server will restart, restoring hover, signature help, completion, and other language features !

## Development

> You need to follow the installation steps before proceeding with this section.

### 1. Prerequisites

You need to have Node.js 20 or later and npm installed on your system :

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Check installation
node -v
npm -v
```

### 2. Installing dependencies

1. Clone the repository :

```bash
git clone https://github.com/simvia-tech/vs-code-aster.git
```

2. Install packages :

```bash
npm install
```

3. Compile extension :

```bash
npm run compile
```

### 3. Running the extension locally

You can press `F5` or go to `Run > Start Debugging` to launch a new VS Code window running this extension.
After making changes, you can reload the new window using `Ctrl` + `R`.

## Telemetry

**VS Code Aster** includes optional telemetry features to help improve the tool by collecting anonymous usage data.

By default, usage tracking is enabled, sending anonymous data about which features you use. You can disable this tracking if you prefer.

To deactivate telemetry :

1. Open VS Code Settings (`File > Preferences > Settings` or `Ctrl + ,` / `Cmd + ,`)
2. Search for `VS Code Aster` in the settings search bar
3. Find the setting `Enable Telemetry` and uncheck it

Telemetry respects your privacy and does not collect sensitive information.

## Contributing

Please check out our [CONTRIBUTING.md](./CONTRIBUTING.md) file if you want to contribute to the project.

Thank you to all our contributors :

- Hadrien Riols - [Email](mailto:hadrien.riols@gmail.com)
- Basile Marchand - [Email](mailto:basile.marchand@simvia.tech)
- Ulysse Bouchet - [Email](mailto:ulysse.bouchet@simvia.tech) - [Website](https://ulyssebouchet.fr)

## See Also

- [Cave's GitHub repository](https://github.com/simvia-tech/cave)
- [Simvia's website](https://simvia.tech)

## License

This project is licensed under the GNU General Public License version 3 (GPL-3.0).
See the full license text in the [LICENSE](./LICENSE) file.

- **Summary:** You are free to use, copy, modify, and redistribute this software.
- **Conditions:** Redistributions and derivative works must be licensed under GPL-3.0 and include source or a written offer to provide the source.
- **More information:** https://www.gnu.org/licenses/gpl-3.0.en.html

## Contact Us

Contact us at [ulysse.bouchet@simvia.tech](mailto:ulysse.bouchet@simvia.tech) or [basile.marchand@simvia.tech](mailto:basile.marchand@simvia.tech).
