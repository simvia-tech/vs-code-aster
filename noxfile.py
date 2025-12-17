import nox
import pathlib as pl
import os 
import shutil 

PREFIX="./python/lsp"

def _install_bundle(session: nox.Session) -> None:
    session.install(
        "-t",
        "./python/bundled/libs",
        "--no-cache-dir",
        "--upgrade",
        "-r",
        "./requirements.txt",
    )


@nox.session(python=["3.11", "3.12"])
def bundle(session):
    """Installs the libraries that will be bundled with the extension."""
    session.install("wheel")
    _install_bundle(session)



@nox.session(python=["3.11", "3.12"])
def package(session):
    """Installs the libraries that will be bundled with the extension."""
    session.install("wheel")
    _install_bundle(session)

    # Crée le paquet .vsix avec vsce
    # Assurez-vous que vsce est installé globalement (npm install -g @vscode/vsce)
    session.run("npx", "vsce", "package", "--skip-license", "--allow-missing-repository", external=True)


# @nox.session(python=False)
# def package(session):
#     """
#     Crée le bundle .vsix en incluant le serveur pygls.
#     """
#     session.run("python", "-m", "venv", f"{PREFIX}/.venv", external=True)
    
#     # 2. Installe pygls et les dépendances du serveur dans l'environnement temporaire
#     session.run(f"{PREFIX}/.venv/bin/pip", "install", "-r", "requirements.txt", external=True)
    
#     # 3. Supprime les fichiers inutiles pour le bundle final
#     venv_path = f"{PREFIX}/.venv"
#     lib_path = pl.Path(venv_path) /"lib"
    
#     # Cherche le dossier pythonX.Y (e.g., python3.9)
#     python_version_dir = [d for d in os.listdir(lib_path) if d.startswith("python")][0]
#     site_packages_path = os.path.join(lib_path, python_version_dir, "site-packages")

#     # Liste les dossiers à supprimer (pip, setuptools, wheel, etc.)
#     packages_to_delete = ["pip", "pip-", "setuptools", "wheel"]

#     # Parcours les dossiers et les supprime
#     for item in os.listdir(site_packages_path):
#         if any(item.startswith(p) for p in packages_to_delete):
#             full_path = os.path.join(site_packages_path, item)
#             session.run("rm", "-r", full_path, external=True)
#             session.log(f"Removed {full_path}")


#     # Note: Adaptez les chemins et les commandes en fonction de la structure de votre projet.