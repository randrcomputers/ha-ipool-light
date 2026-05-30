"""Home Assistant services — effects without select entities."""

from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import entity_registry as er

from .const import DATA_CONNECTION, DATA_LIGHT_ENTITY, DOMAIN
from .effects import EFFECT_NAME_TO_MODE
from .light import IpoolLightEntity

_LOGGER = logging.getLogger(__name__)

SERVICE_SET_RGB_EFFECT = "set_rgb_effect"
SERVICE_SET_EFFECT_SPEED = "set_effect_speed"

SERVICE_SET_RGB_EFFECT_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Required("effect"): vol.In(list(EFFECT_NAME_TO_MODE.keys())),
        vol.Optional("turn_on_first", default=True): bool,
        vol.Optional("speed"): vol.All(vol.Coerce(int), vol.Range(min=1, max=10)),
    }
)

SERVICE_SET_EFFECT_SPEED_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Required("speed"): vol.All(vol.Coerce(int), vol.Range(min=1, max=10)),
    }
)


def _entry_id_for_light_entity(ent) -> str | None:
    """Resolve config entry id from registry (config_entry_id or ``{id}_light`` unique_id)."""
    if ent.config_entry_id:
        return ent.config_entry_id
    uid = ent.unique_id
    if uid and uid.endswith("_light"):
        return uid[: -len("_light")]
    return None


def _light_entity(hass: HomeAssistant, entity_id: str) -> IpoolLightEntity:
    registry = er.async_get(hass)
    ent = registry.async_get(entity_id)
    if ent is None:
        raise ServiceValidationError(f"Unknown entity: {entity_id}")
    entry_id = _entry_id_for_light_entity(ent)
    if entry_id is None:
        raise ServiceValidationError(
            f"{entity_id} is not linked to an iPool Light config entry"
        )
    entry = hass.config_entries.async_get_entry(entry_id)
    if entry is None or entry.domain != DOMAIN:
        raise ServiceValidationError(f"{entity_id} is not an iPool Light entity")
    bucket = hass.data.get(DOMAIN, {}).get(entry_id)
    if not bucket or not bucket.get(DATA_CONNECTION):
        raise HomeAssistantError("iPool Light is not loaded")
    light = bucket.get(DATA_LIGHT_ENTITY)
    if not isinstance(light, IpoolLightEntity):
        raise ServiceValidationError(f"{entity_id} is not an iPool Light entity")
    return light


async def _async_set_rgb_effect(call: ServiceCall) -> None:
    hass = call.hass
    entity_ids: list[str] = cv.ensure_list(call.data[ATTR_ENTITY_ID])
    effect: str = call.data["effect"]
    turn_on_first: bool = call.data["turn_on_first"]
    speed = call.data.get("speed")
    for entity_id in entity_ids:
        light = _light_entity(hass, entity_id)
        await light.async_apply_effect(
            effect, speed=speed, turn_on_first=turn_on_first
        )
        _LOGGER.debug(
            "iPool Light %s: effect %s (mode %s, speed %s)",
            entity_id,
            effect,
            EFFECT_NAME_TO_MODE[effect],
            light._effect_speed,
        )


async def _async_set_effect_speed(call: ServiceCall) -> None:
    hass = call.hass
    entity_ids: list[str] = cv.ensure_list(call.data[ATTR_ENTITY_ID])
    speed: int = call.data["speed"]
    for entity_id in entity_ids:
        light = _light_entity(hass, entity_id)
        await light.async_set_effect_speed(speed)
        _LOGGER.debug("iPool Light %s: effect speed %s", entity_id, speed)


@callback
def async_register_services(hass: HomeAssistant) -> None:
    """Register domain services (re-register so schema updates apply after upgrades)."""
    if hass.services.has_service(DOMAIN, SERVICE_SET_RGB_EFFECT):
        hass.services.async_remove(DOMAIN, SERVICE_SET_RGB_EFFECT)
    if hass.services.has_service(DOMAIN, SERVICE_SET_EFFECT_SPEED):
        hass.services.async_remove(DOMAIN, SERVICE_SET_EFFECT_SPEED)
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_RGB_EFFECT,
        _async_set_rgb_effect,
        schema=SERVICE_SET_RGB_EFFECT_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_EFFECT_SPEED,
        _async_set_effect_speed,
        schema=SERVICE_SET_EFFECT_SPEED_SCHEMA,
    )


@callback
def async_unregister_services(hass: HomeAssistant) -> None:
    """Remove domain services when integration unloads."""
    if hass.services.has_service(DOMAIN, SERVICE_SET_RGB_EFFECT):
        hass.services.async_remove(DOMAIN, SERVICE_SET_RGB_EFFECT)
    if hass.services.has_service(DOMAIN, SERVICE_SET_EFFECT_SPEED):
        hass.services.async_remove(DOMAIN, SERVICE_SET_EFFECT_SPEED)
