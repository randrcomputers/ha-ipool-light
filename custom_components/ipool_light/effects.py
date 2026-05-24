"""RGB animation presets from iPool Light 1.0.3 ``rgb_mode`` (``setRgbMode``)."""

from __future__ import annotations

RGB_EFFECTS: list[tuple[str, int]] = [
    ("Static red", 128),
    ("Static blue", 129),
    ("Static green", 130),
    ("Static cyan", 131),
    ("Static yellow", 132),
    ("Static purple", 133),
    ("Static white", 134),
    ("Tricolor jump", 135),
    ("Seven-color jump", 136),
    ("Tricolor gradient", 137),
    ("Seven-color gradient", 138),
    ("Red gradient", 139),
    ("Green gradient", 140),
    ("Blue gradient", 141),
    ("Yellow gradient", 142),
    ("Cyan gradient", 143),
    ("Purple gradient", 144),
    ("White gradient", 145),
    ("Red-Green gradient", 146),
    ("Red-Blue gradient", 147),
    ("Green-Blue gradient", 148),
    ("Seven-color flash", 149),
    ("Red flash", 150),
    ("Green flash", 151),
    ("Blue flash", 152),
    ("Yellow flash", 153),
    ("Cyan flash", 154),
    ("Purple flash", 155),
    ("White flash", 156),
]

EFFECT_NAME_TO_MODE: dict[str, int] = dict(RGB_EFFECTS)
