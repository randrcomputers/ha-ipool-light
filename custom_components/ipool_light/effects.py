"""RGB / CT / dim presets from iPool Light 1.0.3 ``arrays.xml`` (resolved via APK resources).

``@com.lpoolight:array/rgb_mode`` — ``NetConnectBle.setRgbMode`` (see ``protocol.frame_rgb_mode``).
``ct_mode`` / ``dm_mode`` — ``setColorWarmModel`` / ``setDimModel`` (optional extra selects).
"""

from __future__ import annotations

# rgb_mode: "Label,modeId" from APK ``get_resolved_res_configs(0x7f020004)`` (first locale block).
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

# ct_mode @com.lpoolight:array/ct_mode — warm/cool balance presets (setColorWarmModel).
CT_PRESETS: list[tuple[str, int]] = [
    ("Warm 0% Cool 100%", 128),
    ("Warm 10% Cool 90%", 129),
    ("Warm 20% Cool 80%", 130),
    ("Warm 30% Cool 70%", 131),
    ("Warm 40% Cool 60%", 132),
    ("Warm 50% Cool 50%", 133),
    ("Warm 60% Cool 40%", 134),
    ("Warm 70% Cool 30%", 135),
    ("Warm 80% Cool 20%", 136),
    ("Warm 90% Cool 10%", 137),
    ("Warm 100% Cool 0%", 138),
]

# dm_mode @com.lpoolight:array/dm_mode — dim curve presets (setDimModel).
DIM_PRESETS: list[tuple[str, int]] = [
    ("Dim 0%", 128),
    ("Dim 10%", 129),
    ("Dim 20%", 130),
    ("Dim 30%", 131),
    ("Dim 40%", 132),
    ("Dim 50%", 133),
    ("Dim 60%", 134),
    ("Dim 70%", 135),
    ("Dim 80%", 136),
    ("Dim 90%", 137),
    ("Dim 100%", 138),
]
