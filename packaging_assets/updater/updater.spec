# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller 6 one-file build specification for the elevated yt-dlp updater."""

from pathlib import Path

from PyInstaller.utils.hooks import collect_all


SPEC_DIR = Path(SPECPATH).resolve()
PROJECT_ROOT = SPEC_DIR.parent.parent
SOURCE_ROOT = PROJECT_ROOT / "src"
ENTRY_POINT = SOURCE_ROOT / "utils" / "ytdlp_update" / "updater.py"
ICON_FILE = PROJECT_ROOT / "_internal" / "jtp.ico"


def require_file(path, description):
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Missing {description}: {path}")
    return path


require_file(ENTRY_POINT, "updater entry point")
require_file(ICON_FILE, "application icon")

# rpgp-py exposes the openpgp package and a native _openpgp extension.
# Collect the complete package so the one-file build contains both layers.
openpgp_datas, openpgp_binaries, openpgp_hiddenimports = collect_all("openpgp")


a = Analysis(
    [str(ENTRY_POINT)],
    pathex=[str(SOURCE_ROOT)],
    binaries=openpgp_binaries,
    datas=openpgp_datas,
    hiddenimports=openpgp_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

# Supplying binaries and datas directly to EXE creates a one-file executable.
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="JatubePlayer_updater",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ICON_FILE),
)