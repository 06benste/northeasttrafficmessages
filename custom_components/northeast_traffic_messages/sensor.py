"""Sensor platform for Northeast Traffic Messages."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import SIGN_SETTING_REASONS
from .coordinator import NortheastTrafficMessagesCoordinator, VmsCoordinatorData
from .entity import NortheastTrafficMessagesEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors for a VMS sign."""
    coordinator: NortheastTrafficMessagesCoordinator = entry.runtime_data
    async_add_entities(
        NortheastTrafficMessagesSensor(coordinator, description)
        for description in SENSOR_DESCRIPTIONS
    )


class NortheastTrafficMessagesSensor(NortheastTrafficMessagesEntity, SensorEntity):
    """Sensor for one UTMC VMS data field."""

    def __init__(
        self,
        coordinator: NortheastTrafficMessagesCoordinator,
        description: SensorDescription,
    ) -> None:
        super().__init__(coordinator, description.key)
        self._description = description
        self._attr_device_class = description.device_class
        self._attr_state_class = description.state_class
        if description.options:
            self._attr_options = list(description.options)

    @property
    def native_value(self) -> str | datetime | None:
        """Return sensor value from coordinator data."""
        return self._description.value_fn(self.coordinator.data)


class SensorDescription:
    """Metadata for a sensor entity."""

    def __init__(
        self,
        key: str,
        value_fn: Callable[[VmsCoordinatorData], str | datetime | None],
        *,
        device_class: SensorDeviceClass | None = None,
        state_class: SensorStateClass | None = None,
        options: tuple[str, ...] | None = None,
    ) -> None:
        self.key = key
        self.value_fn = value_fn
        self.device_class = device_class
        self.state_class = state_class
        self.options = options


def _display_text(data: VmsCoordinatorData) -> str:
    return data.display_text


def _last_updated(data: VmsCoordinatorData) -> datetime | None:
    if data.vms.dynamic is None:
        return None
    return data.vms.dynamic.last_updated


def _sign_setting_reason(data: VmsCoordinatorData) -> str | None:
    if data.vms.dynamic is None:
        return None
    return data.vms.dynamic.sign_setting_reason


def _location(data: VmsCoordinatorData) -> str | None:
    return data.vms.static.long_description


SENSOR_DESCRIPTIONS: tuple[SensorDescription, ...] = (
    SensorDescription("message_text", _display_text),
    SensorDescription(
        "last_updated",
        _last_updated,
        device_class=SensorDeviceClass.TIMESTAMP,
    ),
    SensorDescription(
        "sign_setting_reason",
        _sign_setting_reason,
        device_class=SensorDeviceClass.ENUM,
        options=SIGN_SETTING_REASONS,
    ),
    SensorDescription("location", _location),
)
