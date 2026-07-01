# -*- mode: python ; coding: utf-8 -*-
import escpos
import os

escpos_capabilities = os.path.join(os.path.dirname(escpos.__file__), "capabilities.json")

a = Analysis(
    ['src/main.py'],
    pathex=['src'],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        (escpos_capabilities, 'escpos'),
    ],
    hiddenimports=['escpos', 'escpos.printer', 'escpos.printer.win32raw', 'win32print', 'win32ui'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Label_Printer',
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
    icon=['assets/tag.ico'],
)
