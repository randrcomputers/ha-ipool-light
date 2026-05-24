"""Select presets matching iPool Light 1.0.3 resource arrays (``effects.py``)."""

from __future__ import annotations

from collections.abc import Callable

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .connection import IpoolLightConnection
from .const import DATA_CONNECTION, DOMAIN
from .device import device_info_for_entry
from .effects import CT_PRESETS, DIM_PRESETS, RGB_EFFECTS
from .protocol import frame_color_warm_model, frame_dim_model, frame_rgb_mode


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add preset selects (only loaded when enabled in integration options)."""
    session: IpoolLightConnection = hass.data[DOMAIN][entry.entry_id][DATA_CONNECTION]
    info = device_info_for_entry(entry)
    eid = entry.entry_id
    async_add_entities(
        [
            IpoolPresetSelectEntity(
                session,
                entry_id=eid,
                device_info=info,
                translation_key="rgb_effect",
                unique_suffix="rgb_effect",
                presets=RGB_EFFECTS,
                build_frame=frame_rgb_mode,
            ),
            IpoolPresetSelectEntity(
                session,
                entry_id=eid,
                device_info=info,
                translation_key="warm_cool",
                unique_suffix="warm_cool",
                presets=CT_PRESETS,
                build_frame=frame_color_warm_model,
                entity_category=EntityCategory.CONFIG,
            ),
            IpoolPresetSelectEntity(
                session,
                entry_id=eid,
                device_info=info,
                translation_key="dim_curve",
                unique_suffix="dim_curve",
                presets=DIM_PRESETS,
                build_frame=frame_dim_model,
                entity_category=EntityCategory.CONFIG,
            ),
        ],
        update_before_add=False,
    )


class IpoolPresetSelectEntity(SelectEntity):
    """Assumed-state select: sends LedBle frame for chosen preset."""

    _attr_should_poll = False
    _attr_has_entity_name = True

    def __init__(
        self,
        connection: IpoolLightConnection,
        *,
        entry_id: str,
        device_info: DeviceInfo,
        translation_key: str,
        unique_suffix: str,
        presets: list[tuple[str, int]],
        build_frame: Callable[[int], bytes],
        entity_category: EntityCategory | None = None,
    ) -> None:
        self._connection = connection
        self._entry_id = entry_id
        self._presets = presets
        self._build_frame = build_frame
        self._label_to_mode = {label: mode for label, mode in presets}
        self._attr_translation_key = translation_key
        self._attr_unique_id = f"{entry_id}_{unique_suffix}"
        self._attr_options = [label for label, _ in presets]
        self._attr_current_option: str | None = None
        self._attr_device_info = device_info
        if entity_category is not None:
            self._attr_entity_category = entity_category

    async def async_select_option(self, option: str) -> None:
        mode = self._label_to_mode.get(option)
        if mode is None:
            raise HomeAssistantError(f"Unknown option: {option}")
        await self._connection.async_send_frame(self._build_frame(mode))
        self._attr_current_option = option
