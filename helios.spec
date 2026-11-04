from pathlib import Path

project_root = Path(SPECPATH).resolve()

assets_path = project_root / "assets"

if not assets_path.is_dir():
    raise FileNotFoundError(
        f"No se encuentra la carpeta de recursos: {assets_path}"
    )

resources_path = project_root / "helios" / "resources"

if not resources_path.is_dir():
    raise FileNotFoundError(
        f"No se encuentra la carpeta de recursos: {resources_path}"
    )

datas = [
    (str(assets_path), "assets"),
    (str(resources_path), "helios/resources"),
]

a = Analysis(
    [str(project_root / "main.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
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
    [],
    exclude_binaries=True,
    name="Helios",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="Helios",
)
