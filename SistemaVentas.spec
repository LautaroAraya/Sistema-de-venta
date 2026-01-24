# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('firebase_config.py', '.'),
        ('version.txt', '.'),
        ('serviceAccountKey.json', '.'),
        ('serviceAccountKey.json.example', '.'),
        ('assets/*', 'assets'),
        ('logs/*', 'logs'),
        ('requirements.txt', '.'),
        ('database/*', 'database'),
        ('installer/*', 'installer'),
        ('views/*', 'views'),
        ('models/*', 'models'),
        ('utils/*', 'utils'),
        # Agrega aquí cualquier otro archivo/carpeta que tu app necesite en runtime
    ],
    hiddenimports=['requests', 'urllib3', 'certifi'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['pkg_resources'],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='SistemaVentas',
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
    icon=['assets\\logoinstalador.ico'],
)
