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


def frame_rgb_mode(mode: int, speed: int | None = None) -> bytes:
    """``NetConnectBle.setRgbMode`` — animated / static RGB presets (mode 128…156).

    APK 9-byte layout: ``(126, 5, 3, mode, 3, pad, 255, 0, 239)``

    Byte index **4** must be **3** (rgb mode — not speed). Optional ``speed`` may use
    byte index **5** (APK default ``255``).
    """
    m = int(mode) & 0xFF
    b5 = 255
    if speed is not None:
        b5 = max(1, min(10, int(speed)))
    return _pack9((126, 5, 3, m, 3, b5, 255, 0, 239))


def frame_color_warm_model(mode: int) -> bytes:
    """``NetConnectBle.setColorWarmModel`` — warm/cool balance (``ct_mode``)."""
    m = int(mode) & 0xFF
    return _pack9((126, 5, 3, m, 2, 255, 255, 0, 239))


def frame_dim_model(mode: int) -> bytes:
    """``NetConnectBle.setDimModel`` — dimming curve (``dm_mode``)."""
    m = int(mode) & 0xFF
    return _pack9((126, 5, 3, m, 1, 255, 255, 0, 239))
