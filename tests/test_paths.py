
from pathlib import Path

import pytest

from helios.utils import paths


def test_resource_path_uses_project_root_in_development(
    tmp_path,
    monkeypatch,
):
    project_root = tmp_path / "helios_project"
    fake_module = (
        project_root
        / "helios"
        / "utils"
        / "paths.py"
    )

    monkeypatch.setattr(
        paths,
        "__file__",
        str(fake_module),
    )
    monkeypatch.setattr(
        paths.sys,
        "frozen",
        False,
        raising=False,
    )

    result = paths.resource_path("assets/Logo_Helios.png")

    assert result == project_root / "assets" / "Logo_Helios.png"


def test_resource_path_uses_pyinstaller_directory(monkeypatch):
    bundle_directory = Path("/tmp/helios_bundle")

    monkeypatch.setattr(paths.sys, "frozen", True, raising=False)
    monkeypatch.setattr(paths.sys, "_MEIPASS", str(bundle_directory), raising=False)

    result = paths.resource_path("assets/Logo_Helios.png")

    assert result == bundle_directory / "assets" / "Logo_Helios.png"


def test_resource_path_preserves_absolute_paths(tmp_path):
    absolute_path = tmp_path / "resource.txt"

    result = paths.resource_path(absolute_path)

    assert result == absolute_path


@pytest.mark.parametrize(
    ("platform", "environment"),
    [
        (
            "win32",
            {"LOCALAPPDATA": "C:/Users/test/AppData/Local"},
        ),
        (
            "darwin",
            {},
        ),
        (
            "linux",
            {"XDG_DATA_HOME": "/home/test/.local/share"},
        ),
        (
            "linux",
            {},
        ),
    ],
)
def test_user_data_path_resolves_platform_directory(
    tmp_path,
    monkeypatch,
    platform,
    environment,
):
    monkeypatch.setattr(paths.sys, "platform", platform)

    for variable in ("LOCALAPPDATA", "XDG_DATA_HOME"):
        monkeypatch.delenv(variable, raising=False)

    for variable, value in environment.items():
        monkeypatch.setenv(variable, value)

    if platform == "win32":
        expected_path = tmp_path / "Helios"
        monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    elif platform == "darwin":
        expected_path = tmp_path / "Library" / "Application Support" / "Helios"
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
    elif "XDG_DATA_HOME" in environment:
        expected_path = Path(environment["XDG_DATA_HOME"]) / "Helios"
    else:
        expected_path = tmp_path / ".local" / "share" / "Helios"
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

    result = paths.user_data_path()

    assert result == expected_path
    assert result.is_dir()


def test_user_data_path_creates_nested_subdirectories(tmp_path, monkeypatch):
    monkeypatch.setattr(paths.sys, "platform", "win32")
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))

    result = paths.user_data_path("cache/solar")

    assert result == tmp_path / "Helios" / "cache" / "solar"
    assert result.is_dir()


def test_user_data_path_without_relative_path_returns_application_directory(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(paths.sys, "platform", "win32")
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))

    result = paths.user_data_path()

    assert result == tmp_path / "Helios"
    assert result.is_dir()
