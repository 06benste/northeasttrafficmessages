"""Data update coordinator."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    CannotConnect,
    InvalidAuth,
    UTMCApiClient,
    VmsData,
    VmsStatic,
    create_client,
    display_lines,
    display_text,
)
from .const import (
    CONF_FRIENDLY_SIGN_ID,
    CONF_PASSWORD,
    CONF_SIGN_ID,
    CONF_USERNAME,
    DOMAIN,
    MANUFACTURER,
    SCAN_INTERVAL_SECONDS,
)
from .vms_display import VmsDisplayOptions, render_vms_gif_bytes

_LOGGER = logging.getLogger(__name__)


@dataclass
class VmsCoordinatorData:
    """Coordinator payload including rendered GIF bytes."""

    vms: VmsData
    display_lines: list[str]
    display_text: str
    gif_bytes: bytes


class NortheastTrafficMessagesCoordinator(DataUpdateCoordinator[VmsCoordinatorData]):
    """Fetch VMS data from UTMC."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        client: UTMCApiClient,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=SCAN_INTERVAL_SECONDS),
            config_entry=entry,
        )
        self.client = client
        self.sign_id = entry.data[CONF_SIGN_ID]

    async def _async_update_data(self) -> VmsCoordinatorData:
        """Refresh dynamic data every poll; static metadata uses a shared 24-hour cache."""
        try:
            vms = await self.client.async_get_sign_data(self.sign_id)
            lines = display_lines(vms.dynamic)
            text = display_text(vms.dynamic)
            lanterns_on = vms.dynamic is not None and vms.dynamic.lantern_state == 1
            options = VmsDisplayOptions(
                lanterns_on=lanterns_on,
                sign_id=self.sign_id,
                sign_name=vms.static.short_description,
            )
            gif_bytes = await self.hass.async_add_executor_job(
                render_vms_gif_bytes,
                lines,
                options,
            )
            await self._async_update_device(vms.static)
            return VmsCoordinatorData(
                vms=vms,
                display_lines=lines,
                display_text=text,
                gif_bytes=gif_bytes,
            )
        except InvalidAuth as err:
            raise ConfigEntryAuthFailed from err
        except CannotConnect as err:
            raise UpdateFailed(str(err)) from err

    async def _async_update_device(self, static: VmsStatic) -> None:
        """Keep device registry name and location in sync with static metadata."""
        device_registry = dr.async_get(self.hass)
        device = device_registry.async_get_device(identifiers={(DOMAIN, self.sign_id)})
        if device is None:
            return

        friendly_sign_id = self.config_entry.data.get(CONF_FRIENDLY_SIGN_ID, self.sign_id)
        update_kwargs: dict[str, object] = {
            "name": static.short_description or friendly_sign_id,
            "manufacturer": MANUFACTURER,
            "model": friendly_sign_id,
            "configuration_url": "https://www.netraveldata.co.uk/?page_id=230",
        }
        if static.latitude is not None and static.longitude is not None:
            update_kwargs["latitude"] = static.latitude
            update_kwargs["longitude"] = static.longitude

        device_registry.async_update_device(device.id, **update_kwargs)


async def async_create_coordinator(
    hass: HomeAssistant, entry: ConfigEntry
) -> NortheastTrafficMessagesCoordinator:
    """Create coordinator and perform initial refresh."""
    client = create_client(
        hass,
        entry.data[CONF_USERNAME],
        entry.data[CONF_PASSWORD],
    )
    coordinator = NortheastTrafficMessagesCoordinator(hass, entry, client)
    await coordinator.async_config_entry_first_refresh()
    return coordinator
