"""Image platform for Northeast Traffic Messages."""

from __future__ import annotations

import asyncio
import logging
from functools import partial

from homeassistant.components.image import ImageEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .coordinator import NortheastTrafficMessagesCoordinator
from .entity import NortheastTrafficMessagesEntity
from .vms_display import VmsDisplayOptions, render_vms_gif_bytes

_LOGGER = logging.getLogger(__name__)


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
        """Initialize the image entity."""
        NortheastTrafficMessagesEntity.__init__(self, coordinator, "display")
        ImageEntity.__init__(self, coordinator.hass)
        self._attr_content_type = "image/gif"
        self._gif_bytes: bytes | None = None
        self._render_signature: tuple[tuple[str, ...], int | None] | None = None
        self._render_lock = asyncio.Lock()

    async def async_added_to_hass(self) -> None:
        """Render the first GIF once the entity is registered."""
        await super().async_added_to_hass()
        await self._async_update_image()

    def _handle_coordinator_update(self) -> None:
        """Schedule a GIF refresh when UTMC data changes."""
        self.hass.async_create_task(self._async_update_image())
        super()._handle_coordinator_update()

    def _current_render_signature(
        self,
    ) -> tuple[tuple[str, ...], int | None] | None:
        """Return a stable key for the current sign display content."""
        if not self.coordinator.data:
            return None
        dynamic = self.coordinator.data.vms.dynamic
        return (
            tuple(self.coordinator.data.display_lines),
            dynamic.lantern_state if dynamic else None,
        )

    async def _async_update_image(self) -> None:
        """Render the GIF in a worker thread when the sign content changes."""
        signature = self._current_render_signature()
        if signature is None:
            return

        async with self._render_lock:
            if signature == self._render_signature:
                return

            data = self.coordinator.data
            dynamic = data.vms.dynamic
            options = VmsDisplayOptions(
                lanterns_on=dynamic is not None and dynamic.lantern_state == 1,
                sign_id=self.coordinator.render_sign_id,
                sign_name=data.vms.static.short_description,
            )
            try:
                gif_bytes = await self.hass.async_add_executor_job(
                    partial(render_vms_gif_bytes, options=options),
                    list(data.display_lines),
                )
            except Exception:
                _LOGGER.exception("Failed to render VMS GIF for %s", self.entity_id)
                return

            self._gif_bytes = gif_bytes
            self._render_signature = signature
            self._attr_image_last_updated = dt_util.utcnow()
            self.async_write_ha_state()

    async def async_image(self) -> bytes | None:
        """Return the latest rendered sign GIF."""
        return self._gif_bytes
