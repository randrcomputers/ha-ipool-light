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
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.util.color import color_hs_to_RGB

from .connection import IpoolLightConnection
from .const import (
    CONF_NAME,
    DATA_CONNECTION,
    DATA_LIGHT_ENTITY,
    DEFAULT_NAME,
    DOMAIN,
)
from .effects import EFFECT_NAME_TO_MODE
from .protocol import (
    frame_brightness,
    frame_rgb,
    frame_rgb_mode,
    frame_turn_off,
    frame_turn_on,
)

_LOGGER = logging.getLogger(__name__)

ATTR_IPOOL_EFFECT = "ipool_effect"
ATTR_IPOOL_EFFECT_SPEED = "ipool_effect_speed"
DEFAULT_EFFECT_SPEED = 3


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add light entity."""
    session: IpoolLightConnection = hass.data[DOMAIN][entry.entry_id][DATA_CONNECTION]
    name = entry.data.get(CONF_NAME) or DEFAULT_NAME
    entity = IpoolLightEntity(session, entry.entry_id, name)
    async_add_entities([entity], update_before_add=False)


class IpoolLightEntity(LightEntity, RestoreEntity):
    """RGB pool light over BLE (assumed state — no notify decode in this version)."""

    _attr_assumed_state = True
    _attr_supported_color_modes = {ColorMode.RGB}
    _attr_color_mode = ColorMode.RGB

    def __init__(
        self, connection: IpoolLightConnection, entry_id: str, name: str
    ) -> None:
        self._connection = connection
        self._entry_id = entry_id
        self._attr_unique_id = f"{entry_id}_light"
        self._attr_name = name
        self._attr_is_on = False
        self._rgb: tuple[int, int, int] = (255, 255, 255)
        self._brightness: int | None = 255
        self._active_effect: str | None = None
        self._effect_speed: int = DEFAULT_EFFECT_SPEED

    async def async_added_to_hass(self) -> None:
        """Restore last effect / speed so the pool light card survives refresh."""
        await super().async_added_to_hass()
        bucket = self.hass.data.get(DOMAIN, {}).get(self._entry_id)
        if bucket is not None:
            bucket[DATA_LIGHT_ENTITY] = self
        if (last_state := await self.async_get_last_state()) is None:
            return
        attrs = last_state.attributes
        effect = attrs.get(ATTR_IPOOL_EFFECT)
        if isinstance(effect, str) and effect not in ("unknown", "unavailable", ""):
            self._active_effect = effect
        speed = attrs.get(ATTR_IPOOL_EFFECT_SPEED)
        if speed is not None:
            try:
                self._effect_speed = max(1, min(10, int(speed)))
            except (TypeError, ValueError):
                pass
        if last_state.state in ("on", "off"):
            self._attr_is_on = last_state.state == "on"
        rgb = attrs.get(ATTR_RGB_COLOR)
        if isinstance(rgb, (list, tuple)) and len(rgb) >= 3:
            self._rgb = (
                int(rgb[0]) & 0xFF,
                int(rgb[1]) & 0xFF,
                int(rgb[2]) & 0xFF,
            )
        br = attrs.get(ATTR_BRIGHTNESS)
        if br is not None:
            try:
                self._brightness = max(1, min(255, int(br)))
            except (TypeError, ValueError):
                pass

    @property
    def rgb_color(self) -> tuple[int, int, int] | None:
        return self._rgb

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            ATTR_IPOOL_EFFECT: self._active_effect,
            ATTR_IPOOL_EFFECT_SPEED: self._effect_speed,
        }

    async def async_apply_effect(
        self,
        effect_name: str,
        *,
        speed: int | None = None,
        turn_on_first: bool = True,
    ) -> None:
        """Run an APK ``rgb_mode`` preset and remember it for the pool light card."""
        mode = EFFECT_NAME_TO_MODE[effect_name]
        if speed is not None:
            self._effect_speed = max(1, min(10, int(speed)))
        if turn_on_first:
            await self._connection.async_send_frame(frame_turn_on())
        await self._connection.async_send_frame(
            frame_rgb_mode(mode, speed)
        )
        self._active_effect = effect_name
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_set_effect_speed(self, speed: int) -> None:
        """Re-send the current effect with a new animation speed."""
        if not self._active_effect:
            self._effect_speed = max(1, min(10, int(speed)))
            self.async_write_ha_state()
            return
        await self.async_apply_effect(
            self._active_effect,
            speed=speed,
            turn_on_first=False,
        )

    def _clear_effect(self) -> None:
        self._active_effect = None

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
            self._clear_effect()
            await self._send_rgb()
            self._attr_is_on = True
            self.async_write_ha_state()
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
            self.async_write_ha_state()
            return

        await self._connection.async_send_frame(frame_turn_on())
        self._rgb = (255, 255, 255)
        self._brightness = 255
        self._clear_effect()
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._connection.async_send_frame(frame_turn_off())
        self._attr_is_on = False
        self.async_write_ha_state()

    async def _send_rgb(self) -> None:
        r, g, b = self._rgb
        await self._connection.async_send_frame(frame_rgb(r, g, b))
