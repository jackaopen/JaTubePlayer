# -*- mode: python ; coding: utf-8 -*-
"""Simple PyInstaller onedir build for JaTubePlayer."""

import ast
import importlib.util
import os
import shutil
import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

SPEC_DIR = Path(SPECPATH).resolve()
PROJECT_ROOT = SPEC_DIR.parent.parent
SOURCE_ROOT = PROJECT_ROOT / "src"
INTERNAL_DIR = PROJECT_ROOT / "_internal"

ENTRY_POINT = SOURCE_ROOT / "JaTubePlayer.py"
ICON_FILE = INTERNAL_DIR / "jtp.ico"
VERSION_FILE = SPEC_DIR / "version.txt"
STREAMLINK_DIR = INTERNAL_DIR / "streamlink"
COLOR_PICKER_DIR = SOURCE_ROOT / "utils" / "color_picker"

REQUIRED_FILES = [
    ENTRY_POINT,
    ICON_FILE,
    VERSION_FILE,
    SOURCE_ROOT / "account" / "WebView2Host.exe",
    PROJECT_ROOT / "user_data" / "config.template.json",
    PROJECT_ROOT / "user_data" / "starred_vid.template.json",
    STREAMLINK_DIR / "bin" / "streamlink.exe",
    COLOR_PICKER_DIR,
    PROJECT_ROOT / "chrome_ext_pack",
    PROJECT_ROOT / "LICENSE",
]

REQUIRED_INTERNAL_FILES = [
    "banner.png",
    "deno.exe",
    "err.wav",
    "ffmpeg.exe",
    "ffprobe.exe",
    "google_login_err_screen.html",
    "google_login_suc_red_page.html",
    "google_login_waiting_page.html",
    "info.wav",
    "jtp.ico",
    "libmpv-2.dll",
    "JaTubePlayer_updater.exe",
    "warn.wav",
    "yt-dlp.exe",
    "yt_dlp",
]

SKIP_DIRS = {
    "__pycache__",
    ".git",
    ".pytest_cache",
    ".mypy_cache",
    "bin",
    "obj",
    "profile",
}

RUNTIME_PACKAGES = [
    "Crypto",
    "Cryptodome",
    "brotli",
    "certifi",
    "curl_cffi",
    "mutagen",
    "requests",
    "secretstorage",
    "urllib3",
    "websockets",
]

WINDOWS_IMPORTS = [
    "PIL._tkinter_finder",
    "ffmpeg.nodes",
    "pynput.keyboard",
    "pystray._win32",
    "pythoncom",
    "pywintypes",
    "win32clipboard",
    "win32com.propsys",
    "win32com.server.policy",
    "win32com.shell",
    "win32con",
    "win32crypt",
    "win32gui",
    "winrt.runtime",
    "winrt.runtime._internals",
    "winrt.windows.data.xml.dom",
    "winrt.windows.foundation",
    "winrt.windows.ui.notifications",
    "winsdk.windows.foundation",
    "winsdk.windows.media",
    "winsdk.windows.media.playback",
    "winsdk.windows.storage.streams",
]

for path in REQUIRED_FILES + [INTERNAL_DIR / name for name in REQUIRED_INTERNAL_FILES]:
    if not path.exists():
        raise FileNotFoundError(f"Required build file is missing: {path}")

def tree_files(source, destination, skip_dirs=SKIP_DIRS):
    '''
    covert source directory to a list of tuples (source_file, destination_dir)
    skip directories in skip_dirs
    '''
    files = []
    for current_dir, directories, filenames in os.walk(source):
        directories[:] = sorted(name for name in directories if name not in skip_dirs)
        relative_dir = Path(current_dir).relative_to(source)
        target_dir = Path(destination) / relative_dir

        for filename in sorted(filenames):
            if not filename.endswith((".pyc", ".pyo")):
                files.append((str(Path(current_dir) / filename), target_dir.as_posix()))
    return files

def project_modules():
    '''
    make a list of all mod in the form of "package.module" for all packages in the project
    eg "utils.log_handle" for utils/log_handle.py
    exclude utils.ytdlp_update.updater 
    '''
    packages = [
        "account",
        "chrome_extension",
        "effect",
        "history_page",
        "loader",
        "notification",
        "system",
        "ui",
        "utils",
        "video_media_control",
    ]
    modules = set()

    for package in packages:
        package_dir = SOURCE_ROOT / package
        if not package_dir.is_dir():
            continue

        for source_file in package_dir.rglob("*.py"):
            if any(part in SKIP_DIRS for part in source_file.parts):
                continue

            parts = list(source_file.relative_to(SOURCE_ROOT).with_suffix("").parts)
            if parts[-1] == "__init__":
                parts.pop()

            module = ".".join(parts)
            if module and module != "utils.ytdlp_update.updater":
                modules.add(module)

    return sorted(modules)


def installed_submodules(package):
    '''
    collect dynamically imported submodules of a package, return as list of strings
    '''
    try:
        installed = importlib.util.find_spec(package) is not None
    except (ImportError, ModuleNotFoundError, ValueError):
        installed = False
    if not installed:
        return []
    return collect_submodules(package, on_error="ignore")


def imported_stdlib_modules(source_dir:Path):
    '''
    Find standard-library imports used by libraries in source_dir. Return as list of strings.
    '''
    imports = set()

    for source_file in source_dir.rglob("*.py"):
        try:
            tree = ast.parse(source_file.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [item.name for item in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                # node level == 0 means absolute import, relative imports are not stdlib
                names = [node.module]
            else:
                continue

            for name in names:
                if name.split(".", 1)[0] in sys.stdlib_module_names:
                    try:
                        if importlib.util.find_spec(name) is not None:
                            imports.add(name)
                    except (ImportError, ModuleNotFoundError, ValueError):
                        pass

    return sorted(imports)


def root_copy_list(data_tuples):
    '''
    Convert data tuples into exact source/destination file paths.
    i.e.
    [(source_file, destination_dir), ...] -> [(source_file, destination_dir/source_file.name), ...]
    '''
    return [
        (Path(source), Path(destination) / Path(source).name)
        for source, destination in data_tuples
    ]


def copy_files(output_dir, files):
    '''
    Copy application-managed files 
    '''
    for source, relative_destination in files:
        destination = Path(output_dir) / relative_destination
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)




# The normal runtime excludes Streamlink so its required bin folder can be
# collected separately without excluding directories named "bin".
root_payload = root_copy_list(
    tree_files(INTERNAL_DIR, "_internal", SKIP_DIRS | {"streamlink", "bin"})
)
root_payload += root_copy_list(
    tree_files(STREAMLINK_DIR, "_internal/streamlink", SKIP_DIRS - {"bin"})
)
root_payload += root_copy_list(
    tree_files(PROJECT_ROOT / "chrome_ext_pack", "chrome_ext_pack")
)
root_payload += [
    (SOURCE_ROOT / "account" / "WebView2Host.exe", Path("account/WebView2Host.exe")),
    (PROJECT_ROOT / "user_data" / "config.template.json", Path("user_data/config.json")),
    (PROJECT_ROOT / "user_data" / "starred_vid.template.json", Path("user_data/starred_vid.json")),
]


datas = [
    (str(PROJECT_ROOT / "LICENSE"), "."),
    *tree_files(COLOR_PICKER_DIR, "utils/color_picker"),
]

for package in ("customtkinter", "sv_ttk", "CTkMessagebox"):
    datas += collect_data_files(package)

# The bundled yt_dlp source imports these packages dynamically.

hiddenimports = (
    project_modules()
    + imported_stdlib_modules(INTERNAL_DIR / "yt_dlp")
    + WINDOWS_IMPORTS
)
for package in RUNTIME_PACKAGES:
    hiddenimports += installed_submodules(package)

if importlib.util.find_spec("yt_dlp_ejs") is not None:
    datas += collect_data_files("yt_dlp_ejs", includes=["**/*.js"])
    hiddenimports += installed_submodules("yt_dlp_ejs")

hiddenimports = sorted(set(hiddenimports))

# Create the analysis object

a = Analysis(
    [str(ENTRY_POINT)],
    pathex=[str(SOURCE_ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["yt_dlp", "yt_dlp.*", "utils.ytdlp_update.updater"],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="JaTubePlayer",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    contents_directory="_dependencies",
    icon=str(ICON_FILE),
    version=str(VERSION_FILE),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="JaTubePlayer",
)

copy_files(coll.name, root_payload)