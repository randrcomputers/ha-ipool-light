"""Select presets matching iPool Light 1.0.3 resource arrays (``effects.py``)."""

from __future__ import annotations

from collections.abc import Callable

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .connection import IpoolLightConnection
from .const import CONF_ADDRESS, CONF_NAME, DATA_CONNECTION, DEFAULT_NAME, DOMAIN
from .effects import CT_PRESETS, DIM_PRESETS, RGB_EFFECTS
from .protocol import frame_color_warm_model, frame_dim_model, frame_rgb_mode


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add preset selects."""
    session: IpoolLightConnection = hass.data[DOMAIN][entry.entry_id][DATA_CONNECTION]
    name = entry.data.get(CONF_NAME) or DEFAULT_NAME
    addr = dr.format_mac(entry.data[CONF_ADDRESS])
    eid = entry.entry_id
    async_add_entities(
        [
            IpoolPresetSelectEntity(
                session,
                entry_id=eid,
                device_name=name,
                address=addr,
                translation_key="rgb_effect",
                unique_suffix="rgb_effect",
                presets=RGB_EFFECTS,
                build_frame=frame_rgb_mode,
            ),
            IpoolPresetSelectEntity(
                session,
                entry_id=eid,
                device_name=name,
                address=addr,
                translation_key="warm_cool",
                unique_suffix="warm_cool",
                presets=CT_PRESETS,
                build_frame=frame_color_warm_model,
            ),
            IpoolPresetSelectEntity(
                session,
                entry_id=eid,
                device_name=name,
                address=addr,
                translation_key="dim_curve",
                unique_suffix="dim_curve",
                presets=DIM_PRESETS,
                build_frame=frame_dim_model,
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
        device_name: str,
        address: str,
        translation_key: str,
        unique_suffix: str,
        presets: list[tuple[str, int]],
        build_frame: Callable[[int], bytes],
    ) -> None:
        self._connection = connection
        self._entry_id = entry_id
        self._device_title = device_name
        self._address = address
        self._presets = presets
        self._build_frame = build_frame
        self._label_to_mode = {label: mode for label, mode in presets}
        self._attr_translation_key = translation_key
        self._attr_unique_id = f"{entry_id}_{unique_suffix}"
        self._attr_options = [label for label, _ in presets]
        self._attr_current_option: str | None = None

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry_id)},
            name=self._device_title,
            manufacturer="LedBle",
            model="iPool Light (BLE)",
            connections={(dr.CONNECTION_BLUETOOTH, self._address)},
        )

    async def async_select_option(self, option: str) -> None:
        mode = self._label_to_mode.get(option)
        if mode is None:
            raise HomeAssistantError(f"Unknown option: {option}")
        await self._connection.async_send_frame(self._build_frame(mode))
        self._attr_current_option = option
