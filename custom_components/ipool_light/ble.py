"""Resolve BLE device for iPool Light via Home Assistant Bluetooth stack."""

from __future__ import annotations

import logging

from bleak.backends.device import BLEDevice
from homeassistant.components import bluetooth
from homeassistant.components.bluetooth import (
    BluetoothScanningMode,
    BluetoothServiceInfoBleak,
    async_process_advertisements,
    async_rediscover_address,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import device_registry as dr

from .const import BLE_ADVERTISEMENT_WAIT_SECONDS, SERVICE_UUID_FILTER

_LOGGER = logging.getLogger(__name__)


def _addr_hex_digits(value: str) -> str:
    return "".join(c for c in value if c in "0123456789abcdefABCDEF").lower()


def _service_uuids_lower(si: BluetoothServiceInfoBleak) -> set[str]:
    return {u.lower() for u in si.service_uuids}


def _ble_device_from_scanners(hass: HomeAssistant, addr: str) -> BLEDevice | None:
    best: tuple[int, BLEDevice] | None = None
    for connectable in (True, False):
        entries = bluetooth.async_scanner_devices_by_address(hass, addr, connectable)
        for entry in entries:
            rssi = entry.advertisement.rssi
            try:
                r = int(rssi)
            except (TypeError, ValueError):
                r = -999
            cand = entry.ble_device
            if best is None or r > best[0]:
                best = (r, cand)
    return best[1] if best else None


def _ble_device_from_discovered(hass: HomeAssistant, addr: str) -> BLEDevice | None:
    want = _addr_hex_digits(addr)
    if len(want) != 12:
        return None
    want_l = dr.format_mac(addr).lower()
    filt = SERVICE_UUID_FILTER.lower()

    def pick(require_service: bool, connectable: bool) -> BLEDevice | None:
        best: tuple[int, BluetoothServiceInfoBleak] | None = None
        for si in bluetooth.async_discovered_service_info(
            hass, connectable=connectable
        ):
            addr_d = si.address.lower()
            name_d = _addr_hex_digits(si.name or "")
            if addr_d != want_l and name_d != want:
                continue
            if require_service and filt not in _service_uuids_lower(si):
                continue
            try:
                rssi = int(si.rssi) if si.rssi is not None else -999
            except (TypeError, ValueError):
                rssi = -999
            if best is None or rssi > best[0]:
                best = (rssi, si)
        return best[1].device if best else None

    for connectable in (True, False):
        dev = pick(True, connectable) or pick(False, connectable)
        if dev is not None:
            return dev
    return None


async def async_resolve_ble_device(hass: HomeAssistant, address: str) -> BLEDevice:
    """Resolve a Bleak ``BLEDevice`` from HA Bluetooth caches (wait if needed)."""
    addr = dr.format_mac(address.strip())

    ble_device = bluetooth.async_ble_device_from_address(hass, addr, connectable=True)
    if ble_device is None:
        ble_device = bluetooth.async_ble_device_from_address(
            hass, addr, connectable=False
        )
    if ble_device is None:
        ble_device = _ble_device_from_scanners(hass, addr)
    if ble_device is None:
        ble_device = _ble_device_from_discovered(hass, addr)

    if ble_device is None:
        async_rediscover_address(hass, addr)
        _LOGGER.debug(
            "iPool Light %s not in Bluetooth cache; waiting up to %ss",
            addr,
            BLE_ADVERTISEMENT_WAIT_SECONDS,
        )
        try:
            service_info = await async_process_advertisements(
                hass,
                lambda si: si.address.lower() == addr.lower(),
                {"address": addr},
                BluetoothScanningMode.ACTIVE,
                BLE_ADVERTISEMENT_WAIT_SECONDS,
            )
        except TimeoutError as err:
            raise HomeAssistantError(
                f"iPool Light ({addr}) did not advertise within "
                f"{BLE_ADVERTISEMENT_WAIT_SECONDS}s. Move a Bluetooth proxy near "
                "the pool, ensure the light is powered, then check "
                "Settings → Devices & services → Bluetooth."
            ) from err
        ble_device = service_info.device

    return ble_device
