# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('dialogs/resources/images/start_screen.png', 'dialogs/resources/images'),
        ('dialogs/resources/images/favorites_screen.png', 'dialogs/resources/images'),
        ('dialogs/resources/images/file_operations.png', 'dialogs/resources/images'),
        ('dialogs/resources/images/exit_screen.png', 'dialogs/resources/images'),
        ('dialogs/resources/images/search_filters.png', 'dialogs/resources/images'),
        ('dialogs/resources/images/search_screen.png', 'dialogs/resources/images'),
        ('dialogs/resources/images/view_modes.png', 'dialogs/resources/images'),
        ('dialogs/resources/images/folder_operations.png', 'dialogs/resources/images'),
        ('widgets/resources/desktop.ini', 'widgets/resources'),
        ('widgets/resources/loading.gif', 'widgets/resources'),
        ('widgets/resources/folder-management.png', 'widgets/resources'),
        ('widgets/themes/dark_theme.qss', 'widgets/themes'),
    ],

    hiddenimports=[],
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
    name='main',
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
)
