"""The iPool Light (BLE) integration — LedBle protocol from iPool Light Android 1.0.3."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .connection import IpoolLightConnection
from .const import CONF_ADDRESS, DATA_CONNECTION, DOMAIN

PLATFORMS: list[Platform] = [Platform.LIGHT, Platform.SELECT]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up iPool Light from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    session = IpoolLightConnection(hass, entry.data[CONF_ADDRESS])
    hass.data[DOMAIN][entry.entry_id] = {DATA_CONNECTION: session}
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        entry_data = hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
        if entry_data and (session := entry_data.get(DATA_CONNECTION)):
            await session.async_disconnect()
    return unload_ok
