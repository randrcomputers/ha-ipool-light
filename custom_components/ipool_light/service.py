"""Home Assistant services — effects without select entities."""

from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import entity_registry as er

from .connection import IpoolLightConnection
from .const import DATA_CONNECTION, DOMAIN
from .effects import EFFECT_NAME_TO_MODE
from .protocol import frame_rgb_mode, frame_turn_on

_LOGGER = logging.getLogger(__name__)

SERVICE_SET_RGB_EFFECT = "set_rgb_effect"

SERVICE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Required("effect"): vol.In(list(EFFECT_NAME_TO_MODE.keys())),
        vol.Optional("turn_on_first", default=True): bool,
    }
)


def _session_for_light(hass: HomeAssistant, entity_id: str) -> IpoolLightConnection:
    registry = er.async_get(hass)
    ent = registry.async_get(entity_id)
    if ent is None:
        raise ServiceValidationError(f"Unknown entity: {entity_id}")
    if ent.platform != "light" or not ent.config_entry_id:
        raise ServiceValidationError(f"{entity_id} is not an iPool Light entity")
    entry = hass.config_entries.async_get_entry(ent.config_entry_id)
    if entry is None or entry.domain != DOMAIN:
        raise ServiceValidationError(f"{entity_id} is not from {DOMAIN}")
    bucket = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    if not bucket or not (session := bucket.get(DATA_CONNECTION)):
        raise HomeAssistantError("iPool Light is not loaded")
    return session


async def _async_set_rgb_effect(hass: HomeAssistant, call: ServiceCall) -> None:
    entity_ids: list[str] = cv.ensure_list(call.data[ATTR_ENTITY_ID])
    effect: str = call.data["effect"]
    turn_on_first: bool = call.data["turn_on_first"]
    mode = EFFECT_NAME_TO_MODE[effect]
    payload = frame_rgb_mode(mode)
    for entity_id in entity_ids:
        session = _session_for_light(hass, entity_id)
        if turn_on_first:
            await session.async_send_frame(frame_turn_on())
        await session.async_send_frame(payload)
        _LOGGER.debug("iPool Light %s: effect %s (mode %s)", entity_id, effect, mode)


@callback
def async_register_services(hass: HomeAssistant) -> None:
    """Register domain services once."""
    if hass.services.has_service(DOMAIN, SERVICE_SET_RGB_EFFECT):
        return
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_RGB_EFFECT,
        _async_set_rgb_effect,
        schema=SERVICE_SCHEMA,
    )


@callback
def async_unregister_services(hass: HomeAssistant) -> None:
    """Remove domain services when integration unloads."""
    if not hass.services.has_service(DOMAIN, SERVICE_SET_RGB_EFFECT):
        return
    hass.services.async_remove(DOMAIN, SERVICE_SET_RGB_EFFECT)
