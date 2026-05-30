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


def frame_speed(percent: int) -> bytes:
    """``NetConnectBle`` animation speed — separate command (action **02**).

    Same family as brightness (``126, 4, …``). APK uses **0–100** (higher = faster).
    """
    p = max(0, min(100, int(percent)))
    return _pack9((126, 4, 2, p, 255, 255, 255, 0, 239))


def ha_speed_slider_to_wire(speed_1_10: int) -> int:
    """Map pool light card slider (1–10) to APK wire speed (0–100)."""
    s = max(1, min(10, int(speed_1_10)))
    return min(100, max(0, round((s - 1) * 100 / 9)))


def frame_rgb_mode(mode: int) -> bytes:
    """``NetConnectBle.setRgbMode`` — animated / static RGB presets (mode 128…156).

    APK layout: ``(126, 5, 3, mode, 3, 255, 0, 239)``. Speed is **not** in this frame;
    send ``frame_speed`` separately (LedBle action 02).
    """
    m = int(mode) & 0xFF
    return _pack9((126, 5, 3, m, 3, 255, 0, 239))


def frame_color_warm_model(mode: int) -> bytes:
    """``NetConnectBle.setColorWarmModel`` — warm/cool balance (``ct_mode``)."""
    m = int(mode) & 0xFF
    return _pack9((126, 5, 3, m, 2, 255, 255, 0, 239))


def frame_dim_model(mode: int) -> bytes:
    """``NetConnectBle.setDimModel`` — dimming curve (``dm_mode``)."""
    m = int(mode) & 0xFF
    return _pack9((126, 5, 3, m, 1, 255, 255, 0, 239))
