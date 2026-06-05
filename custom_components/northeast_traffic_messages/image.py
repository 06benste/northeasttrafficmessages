"""Image platform for Northeast Traffic Messages."""

from __future__ import annotations

from typing import Any

from homeassistant.components.image import ImageEntity
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
    """Set up image entities for a VMS sign."""
    coordinator: NortheastTrafficMessagesCoordinator = entry.runtime_data
    async_add_entities([VmsDisplayImage(coordinator)])


class VmsDisplayImage(NortheastTrafficMessagesEntity, ImageEntity):
    """Simulated dot-matrix sign face as a GIF."""

    def __init__(self, coordinator: NortheastTrafficMessagesCoordinator) -> None:
        super().__init__(coordinator, "display")
        self._attr_content_type = "image/gif"
        # Initialize access_tokens list required by ImageEntity
        self.access_tokens: list[str] = []

    @property
    def state_attributes(self) -> dict[str, Any] | None:
        """Return state attributes, or None if no access tokens available."""
        if not self.access_tokens:
            return None
        return {"access_token": self.access_tokens[-1]}

    async def async_image(self) -> bytes | None:
        """Return the latest rendered sign GIF."""
        return self.coordinator.data.gif_bytes
