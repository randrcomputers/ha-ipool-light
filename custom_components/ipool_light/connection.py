"""Persistent BLE client for iPool Light (LedBle)."""

from __future__ import annotations

import asyncio
import logging

from bleak import BleakClient
from bleak.exc import BleakError
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .ble import async_resolve_ble_device
from .const import GATT_WRITE_TARGETS

_LOGGER = logging.getLogger(__name__)


class IpoolLightConnection:
    """Single Bleak connection per config entry; writes LedBle 9-byte frames."""

    def __init__(self, hass: HomeAssistant, address: str) -> None:
        self.hass = hass
        self.address = address
        self._lock = asyncio.Lock()
        self._client: BleakClient | None = None
        self._working_char: str | None = None

    @property
    def is_connected(self) -> bool:
        c = self._client
        return c is not None and c.is_connected

    async def async_disconnect(self) -> None:
        async with self._lock:
            await self._disconnect_locked()

    async def _disconnect_locked(self) -> None:
        if self._client is None:
            return
        try:
            if self._client.is_connected:
                await self._client.disconnect()
        except BleakError:
            _LOGGER.debug("disconnect raised BleakError (ignored)", exc_info=True)
        self._client = None

    async def _ensure_connected_locked(self) -> BleakClient:
        if self._client is not None and self._client.is_connected:
            return self._client
        await self._disconnect_locked()
        ble_device = await async_resolve_ble_device(self.hass, self.address)
        client = BleakClient(ble_device, timeout=45.0)
        await client.connect()
        if not client.is_connected:
            raise HomeAssistantError("Failed to connect to iPool Light over BLE")
        self._client = client
        self._working_char = None
        _LOGGER.info("iPool Light: BLE connected (%s)", ble_device.address)
        return client

    async def async_send_frame(self, payload: bytes) -> None:
        """Write the 9-byte frame using the same GATT fallbacks as the Android app."""
        if len(payload) != 9:
            raise ValueError("LedBle payload must be 9 bytes")
        async with self._lock:
            try:
                client = await self._ensure_connected_locked()
                last_err: Exception | None = None

                if self._working_char:
                    try:
                        await client.write_gatt_char(
                            self._working_char, payload, response=True
                        )
                        return
                    except BleakError:
                        self._working_char = None

                for _svc, char_uuid in GATT_WRITE_TARGETS:
                    try:
                        await client.write_gatt_char(
                            char_uuid, payload, response=True
                        )
                        self._working_char = char_uuid
                        return
                    except BleakError as err:
                        last_err = err
                        try:
                            await client.write_gatt_char(
                                char_uuid, payload, response=False
                            )
                            self._working_char = char_uuid
                            return
                        except BleakError as err2:
                            last_err = err2

                await self._disconnect_locked()
                raise HomeAssistantError(
                    "iPool Light: no working GATT write characteristic "
                    "(expected LedBle ffe1 / ffe9 / fff3 on this firmware)."
                ) from last_err
            except BleakError as err:
                await self._disconnect_locked()
                raise HomeAssistantError(f"BLE error: {err}") from err
