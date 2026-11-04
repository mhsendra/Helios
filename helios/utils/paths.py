
import os
import sys
from pathlib import Path


def resource_path(relative_path: str | Path) -> Path:
    """
    Resolve a path to a resource bundled with Helios.

    Supports normal development execution and PyInstaller bundles.
    """
    relative_path = Path(relative_path)

    if relative_path.is_absolute():
        return relative_path

    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).resolve().parents[2]

    return base_path / relative_path


def user_data_path(relative_path: str | Path | None = None) -> Path:
    """
    Resolve a persistent, user-writable application data path.

    The application data directory is created when this function is called.
    """
    if sys.platform == "win32":
        base_path = Path(
            os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")
        ) / "Helios"

    elif sys.platform == "darwin":
        base_path = (
            Path.home()
            / "Library"
            / "Application Support"
            / "Helios"
        )

    else:
        data_home = os.environ.get("XDG_DATA_HOME")

        if data_home:
            base_path = Path(data_home) / "Helios"
        else:
            base_path = Path.home() / ".local" / "share" / "Helios"

    target_path = (
        base_path
        if relative_path is None
        else base_path / Path(relative_path)
    )

    target_path.mkdir(parents=True, exist_ok=True)

    return target_path
