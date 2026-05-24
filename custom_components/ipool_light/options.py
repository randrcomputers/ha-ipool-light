"""Config-entry options."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry

from .const import OPT_EFFECT_SELECTS

DEFAULT_EFFECT_SELECTS = False


def get_integration_options(entry: ConfigEntry) -> dict[str, bool]:
    """Merged options with safe defaults."""
    opts = entry.options
    return {
        OPT_EFFECT_SELECTS: bool(
            opts.get(OPT_EFFECT_SELECTS, DEFAULT_EFFECT_SELECTS)
        ),
    }
