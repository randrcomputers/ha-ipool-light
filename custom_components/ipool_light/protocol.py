"""Wire payloads from iPool Light / LedBle ``NetConnectBle`` (APK 1.0.3).

Each command is nine bytes: the app builds ``int[9]`` and ``Tool.int2bytearray``
concatenates each int as a single low byte (``ByteArrayOutputStream.write(I)``).
"""

from __future__ import annotations


def _pack9(values: tuple[int, ...]) -> bytes:
    if len(values) != 9:
        raise ValueError("LedBle frames are always 9 bytes")
    return bytes(int(v) & 0xFF for v in values)


def frame_turn_on() -> bytes:
    """``NetConnectBle.turnOn``."""
    return _pack9((126, 4, 4, 1, 255, 255, 255, 0, 239))


def frame_turn_off() -> bytes:
    """``NetConnectBle.turnOff``."""
    return _pack9((126, 4, 4, 0, 255, 255, 255, 0, 239))


def frame_rgb(r: int, g: int, b: int) -> bytes:
    """``NetConnectBle.setRgb`` (RGB 0–255)."""
    return _pack9((126, 7, 5, 3, r, g, b, 0, 239))


def frame_brightness(percent: int) -> bytes:
    """``NetConnectBle.setBrightness`` (0–100)."""
    p = max(0, min(100, int(percent)))
    return _pack9((126, 4, 1, p, 255, 255, 255, 0, 239))
