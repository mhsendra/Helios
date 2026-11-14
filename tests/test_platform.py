import sys

import pytest

from helios.utils.platform import is_android


@pytest.mark.parametrize(
    ("platform", "environment", "expected"),
    [
        ("linux", {}, False),
        ("win32", {}, False),
        ("darwin", {}, False),
        ("android", {}, True),
        ("linux", {"ANDROID_ARGUMENT": "/data"}, True),
        ("linux", {"ANDROID_PRIVATE": "/data"}, True),
    ],
)
def test_is_android(monkeypatch, platform, environment, expected):
    monkeypatch.setattr(sys, "platform", platform)

    monkeypatch.delenv("ANDROID_ARGUMENT", raising=False)
    monkeypatch.delenv("ANDROID_PRIVATE", raising=False)

    for name, value in environment.items():
        monkeypatch.setenv(name, value)

    assert is_android() is expected
