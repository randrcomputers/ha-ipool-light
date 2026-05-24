"""Light platform — RGB + brightness via LedBle 9-byte frames (iPool Light 1.0.3)."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_HS_COLOR,
    ATTR_RGB_COLOR,
    ColorMode,
    LightEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.color import color_hs_to_RGB

from .connection import IpoolLightConnection
from .const import CONF_NAME, DATA_CONNECTION, DEFAULT_NAME, DOMAIN
from .protocol import frame_brightness, frame_rgb, frame_turn_off, frame_turn_on

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add light entity."""
    session: IpoolLightConnection = hass.data[DOMAIN][entry.entry_id][DATA_CONNECTION]
    name = entry.data.get(CONF_NAME) or DEFAULT_NAME
    async_add_entities([IpoolLightEntity(session, entry.entry_id, name)], update_before_add=False)


class IpoolLightEntity(LightEntity):
    """RGB pool light over BLE (assumed state — no notify decode in this version)."""

    _attr_assumed_state = True
    _attr_supported_color_modes = {ColorMode.RGB}
    _attr_color_mode = ColorMode.RGB

    def __init__(
        self, connection: IpoolLightConnection, entry_id: str, name: str
    ) -> None:
        self._connection = connection
        self._attr_unique_id = f"{entry_id}_light"
        self._attr_name = name
        self._attr_is_on = False
        self._rgb: tuple[int, int, int] = (255, 255, 255)
        self._brightness: int | None = 255

    @property
    def rgb_color(self) -> tuple[int, int, int] | None:
        return self._rgb

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on or adjust color / brightness."""
        br = kwargs.get(ATTR_BRIGHTNESS)
        rgb = kwargs.get(ATTR_RGB_COLOR)
        if rgb is None and ATTR_HS_COLOR in kwargs:
            hs = kwargs[ATTR_HS_COLOR]
            rgb = color_hs_to_RGB(float(hs[0]), float(hs[1]))

        if rgb is not None:
            r, g, b = (int(x) & 0xFF for x in rgb)
            if br is not None:
                r = int(r * br / 255)
                g = int(g * br / 255)
                b = int(b * br / 255)
            self._rgb = (r, g, b)
            self._brightness = br if br is not None else self._brightness or 255
            await self._send_rgb()
            self._attr_is_on = True
            return

        if br is not None:
            self._brightness = int(br)
            pct = max(1, round(int(br) * 100 / 255))
            try:
                await self._connection.async_send_frame(frame_brightness(pct))
            except HomeAssistantError:
                _LOGGER.warning("Brightness command failed; trying full white on")
                await self._connection.async_send_frame(frame_turn_on())
            self._attr_is_on = True
            return

        await self._connection.async_send_frame(frame_turn_on())
        self._rgb = (255, 255, 255)
        self._brightness = 255
        self._attr_is_on = True

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._connection.async_send_frame(frame_turn_off())
        self._attr_is_on = False

    async def _send_rgb(self) -> None:
        r, g, b = self._rgb
        await self._connection.async_send_frame(frame_rgb(r, g, b))
