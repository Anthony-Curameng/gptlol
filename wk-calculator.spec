# PyInstaller desktop build configuration.
from PyInstaller.utils.hooks import collect_data_files

datas = [("data/authority_rules.json", "data")]
a = Analysis(["main.py"], pathex=[], binaries=[], datas=datas, hiddenimports=[], hookspath=[], hooksconfig={}, runtime_hooks=[], excludes=[])
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, a.binaries, a.datas, [], name="Wk Calculator", debug=False, bootloader_ignore_signals=False, strip=False, upx=True, console=False)
