"""
Build script - Creates a one-click executable using PyInstaller.
Must be run on the target OS (PyInstaller does not cross-compile).
Usage:
    pip install pyinstaller
    python build_installer.py
Output:
    Windows -> dist/OpenQFD.exe
    macOS   -> dist/OpenQFD.app
    Linux   -> dist/OpenQFD
"""
import subprocess, sys, os

APP_NAME = "OpenQFD"
ENTRY = "main.py"
ICON_WIN = os.path.join("assets", "qfd.ico")
ICON_MAC = os.path.join("assets", "qfd.icns")
# NOTE: cloud/ folder is NOT included in the build (admin-only files)
SEP = os.pathsep

def build():
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", APP_NAME,
        "--onefile",
        "--windowed",
        "--noconfirm",
        "--clean",
        f"--add-data=assets{SEP}assets",
        f"--add-data=views{SEP}views",
        f"--add-data=models{SEP}models",
        f"--add-data=engines{SEP}engines",
        f"--add-data=utils{SEP}utils",
        f"--add-data=LICENSE.md{SEP}.",
        "--hidden-import=PySide6.QtWidgets",
        "--hidden-import=PySide6.QtCore",
        "--hidden-import=PySide6.QtGui",
        "--hidden-import=PySide6.QtSvg",
        # matplotlib's compiled C-extension submodules (verified exhaustively by walking
        # the installed matplotlib/ package for every *.pyd file) — --hidden-import for
        # a partial guess of these kept missing one at a time across builds, and the
        # --collect-all/--collect-submodules alternatives pulled in unrelated optional
        # dependencies (Tkinter's Tcl data, or even torch/pandas/scipy/numba this dev
        # box happens to have installed) that bloated the exe to 350MB+. This is the
        # complete list, so nothing is either missing or over-included:
        #   ft2font, _c_internal_utils, _image, _path, _qhull, _tri,
        #   backends/_backend_agg   (all needed; _tkagg deliberately excluded — Qt-only app)
        "--hidden-import=matplotlib.ft2font",
        "--hidden-import=matplotlib._c_internal_utils",
        "--hidden-import=matplotlib._image",
        "--hidden-import=matplotlib._path",
        "--hidden-import=matplotlib._qhull",
        "--hidden-import=matplotlib._tri",
        "--hidden-import=matplotlib.backends._backend_agg",
        "--hidden-import=numpy",
        "--hidden-import=openpyxl",
        "--hidden-import=unicodedata",
        "--hidden-import=stringprep",
        "--hidden-import=encodings",
        # Size audit of the 80MB build (via EXE-00.toc) found several MB-scale
        # dependencies our own code never touches. Excluding the Python binding
        # modules trims the .pyd wrapper (the underlying Qt6*.dll for Quick/Qml/Pdf
        # still gets bundled regardless — apparently a binary-level dependency of
        # PySide6's own hook, not worth chasing further given how fragile this build
        # has already proven to be).
        #   - PySide6.QtQml/QtQuick/QtQuick3D/QtQuickWidgets: this is a QtWidgets-only
        #     app, no QML anywhere.
        #   - PySide6.QtPdf/QtPdfWidgets: no PDF viewing/generation.
        #   - lxml: confirmed genuinely optional in openpyxl (proper try/except
        #     fallback to stdlib xml.etree.ElementTree in openpyxl/xml/functions.py)
        #     and matplotlib doesn't reference it at all.
        #   NOTE: PIL/Pillow was ALSO tried here and had to be reverted — matplotlib
        #   imports it unconditionally in matplotlib/colors.py, so it's a hard
        #   dependency, not optional. Do not exclude it again.
        "--exclude-module=PySide6.QtQml",
        "--exclude-module=PySide6.QtQuick",
        "--exclude-module=PySide6.QtQuick3D",
        "--exclude-module=PySide6.QtQuickWidgets",
        "--exclude-module=PySide6.QtPdf",
        "--exclude-module=PySide6.QtPdfWidgets",
        "--exclude-module=lxml",
    ]
    if sys.platform == "darwin" and os.path.exists(ICON_MAC):
        cmd.append(f"--icon={ICON_MAC}")
    elif os.name == "nt" and os.path.exists(ICON_WIN):
        cmd.append(f"--icon={ICON_WIN}")
    cmd.append(ENTRY)

    print(f"Building {APP_NAME}...\n")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"Build FAILED (code {result.returncode})")
        sys.exit(1)

    if sys.platform == "darwin":
        out = os.path.join("dist", f"{APP_NAME}.app")
    elif os.name == "nt":
        out = os.path.join("dist", f"{APP_NAME}.exe")
    else:
        out = os.path.join("dist", APP_NAME)

    if not os.path.exists(out):
        print("Build completed but output not found.")
        return

    if os.path.isdir(out):
        size_bytes = sum(os.path.getsize(os.path.join(r, f))
                          for r, _, fs in os.walk(out) for f in fs)
    else:
        size_bytes = os.path.getsize(out)
    mb = size_bytes / (1024 * 1024)
    print(f"\n{'='*50}")
    print(f"  BUILD SUCCESS!")
    print(f"  {os.path.abspath(out)}  ({mb:.0f} MB)")
    print(f"{'='*50}")

if __name__ == "__main__":
    build()
