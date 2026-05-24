"""The iPool Light (BLE) integration — LedBle protocol from iPool Light Android 1.0.3."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .connection import IpoolLightConnection
from .const import CONF_ADDRESS, DATA_CONNECTION, DOMAIN, OPT_EFFECT_SELECTS
from .options import get_integration_options

PLATFORMS_BASE: list[Platform] = [Platform.LIGHT]


def _platforms_for_entry(entry: ConfigEntry) -> list[Platform]:
    platforms = list(PLATFORMS_BASE)
    if get_integration_options(entry)[OPT_EFFECT_SELECTS]:
        platforms.append(Platform.SELECT)
    return platforms


async def _async_options_updated(hass: HomeAssistant, entry: ConfigEntry) -> None:
    if entry.state is not ConfigEntryState.LOADED:
        return
    await hass.config_entries.async_reload(entry.entry_id)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up iPool Light from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    session = IpoolLightConnection(hass, entry.data[CONF_ADDRESS])
    hass.data[DOMAIN][entry.entry_id] = {DATA_CONNECTION: session}
    entry.async_on_unload(entry.add_update_listener(_async_options_updated))
    await hass.config_entries.async_forward_entry_setups(
        entry, _platforms_for_entry(entry)
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, _platforms_for_entry(entry)
    )
    if unload_ok:
        entry_data = hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
        if entry_data and (session := entry_data.get(DATA_CONNECTION)):
            await session.async_disconnect()
    return unload_ok
