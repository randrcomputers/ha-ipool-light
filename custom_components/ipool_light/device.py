"""Shared device registry info for light + optional selects."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.entity import DeviceInfo

from .const import CONF_ADDRESS, CONF_NAME, DEFAULT_NAME, DOMAIN


def device_info_for_entry(entry: ConfigEntry) -> DeviceInfo:
    """One BLE device per config entry."""
    name = entry.data.get(CONF_NAME) or DEFAULT_NAME
    address = dr.format_mac(entry.data[CONF_ADDRESS])
    return DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=name,
        manufacturer="LedBle",
        model="iPool Light (BLE)",
        connections={(dr.CONNECTION_BLUETOOTH, address)},
    )
