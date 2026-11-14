"""Detección de la plataforma de ejecución."""

import os
import sys


def is_android() -> bool:
    """Indica si Helios se ejecuta en Android."""
    return (
        sys.platform == "android"
        or "ANDROID_ARGUMENT" in os.environ
        or "ANDROID_PRIVATE" in os.environ
    )
