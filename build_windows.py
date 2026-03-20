from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

APP_NAME = 'ProjectSpacingBoard'
ROOT = Path(__file__).resolve().parent
DIST_DIR = ROOT / 'release'
BUILD_DIR = ROOT / 'build'


def clean_directories() -> None:
    for directory in (DIST_DIR, BUILD_DIR):
        if directory.exists():
            shutil.rmtree(directory)


def build_windows_exe() -> None:
    command = [
        sys.executable,
        '-m',
        'PyInstaller',
        '--noconfirm',
        '--clean',
        '--windowed',
        '--onefile',
        '--name',
        APP_NAME,
        '--distpath',
        str(DIST_DIR),
        '--workpath',
        str(BUILD_DIR),
        str(ROOT / 'app.py'),
    ]
    subprocess.run(command, check=True)


if __name__ == '__main__':
    clean_directories()
    build_windows_exe()
