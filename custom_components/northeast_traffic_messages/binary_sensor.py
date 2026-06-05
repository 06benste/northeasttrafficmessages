"""Binary sensor platform for Northeast Traffic Messages."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import NortheastTrafficMessagesCoordinator
from .entity import NortheastTrafficMessagesEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up binary sensors for a VMS sign."""
    coordinator: NortheastTrafficMessagesCoordinator = entry.runtime_data
    async_add_entities([VmsLanternBinarySensor(coordinator)])


class VmsLanternBinarySensor(NortheastTrafficMessagesEntity, BinarySensorEntity):
    """Report whether the sign lanterns are flashing."""

    def __init__(self, coordinator: NortheastTrafficMessagesCoordinator) -> None:
        super().__init__(coordinator, "lanterns_flashing")
        self._attr_icon = "mdi:traffic-light"

    @property
    def is_on(self) -> bool | None:
        """Return True when UTMC reports lanternState == 1 (flashing)."""
        dynamic = self.coordinator.data.vms.dynamic
        if dynamic is None or dynamic.lantern_state is None:
            return None
        return dynamic.lantern_state == 1
