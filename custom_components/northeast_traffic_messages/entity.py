"""Base entity for Northeast Traffic Messages."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from homeassistant.config_entries import ConfigEntry

from .const import CONF_FRIENDLY_SIGN_ID, DOMAIN, MANUFACTURER
from .coordinator import NortheastTrafficMessagesCoordinator


class NortheastTrafficMessagesEntity(
    CoordinatorEntity[NortheastTrafficMessagesCoordinator]
):
    """Base entity attached to a VMS sign device."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: NortheastTrafficMessagesCoordinator,
        entity_key: str,
    ) -> None:
        super().__init__(coordinator)
        self.entity_key = entity_key
        self._attr_unique_id = f"{coordinator.sign_id}_{entity_key}"
        self._attr_translation_key = entity_key

    @property
    def _config_entry(self) -> ConfigEntry:
        """Return the config entry backing this coordinator."""
        assert self.coordinator.config_entry is not None
        return self.coordinator.config_entry

    @property
    def _friendly_sign_id(self) -> str:
        """Return the user-facing sign code stored at setup time."""
        return (
            self._config_entry.data.get(CONF_FRIENDLY_SIGN_ID)
            or self.coordinator.sign_id
        )

    @property
    def device_info(self) -> DeviceInfo:
        """Link entity to the VMS sign device."""
        static = self.coordinator.data.vms.static
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.sign_id)},
            name=static.short_description or self._friendly_sign_id,
            manufacturer=MANUFACTURER,
            model=self._friendly_sign_id,
            configuration_url="https://www.netraveldata.co.uk/?page_id=230",
        )
