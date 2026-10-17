# -*- mode: python ; coding: utf-8 -*-

from platform import system as platform_system

# Set icon based on platform
if platform_system().lower() == 'windows':
    icon_file = './assets/app_icon.ico'
elif platform_system().lower() == 'darwin':  # macOS
    icon_file = './assets/app_icon.icns'
else:  # Linux
    icon_file = './assets/app_icon.png'


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['PIL._tkinter_finder'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)
splash = Splash(
    './assets/app_splash.jpg',
    binaries=a.binaries,
    datas=a.datas,
    text_pos=(10,367),
    text_size=12,
    text_color='#6599b2',
    minify_script=True,
    always_on_top=True,
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    splash,
    splash.binaries,
    [],
    name='MiMoQuant',
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
    icon=[icon_file],
)


import shutil
from os import path

folders_to_copy = [
    './assets',
    './analyzers/yolox/models',
]

for source_folder in folders_to_copy:
    clean_relative_path = os.path.normpath(source_folder).lstrip('.' + os.sep)
    destination_folder = os.path.join(DISTPATH, clean_relative_path)
    parent_dir = os.path.dirname(destination_folder)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)
    if os.path.exists(destination_folder):
        shutil.rmtree(destination_folder)
    if os.path.exists(source_folder):
        shutil.copytree(source_folder, destination_folder)
        print(f"Successfully copied '{source_folder}' to '{destination_folder}'")
    else:
        print(f"Warning: Source folder '{source_folder}' not found. Skipping.")