"""Suptronics UPS X120x integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .coordinator import SuptronicsUPSCoordinator
from .const import DOMAIN
from .options import merge_options

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.NUMBER,
    Platform.SENSOR,
    Platform.SWITCH,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Suptronics UPS from a config entry."""
    merged_options = merge_options(entry.options)
    if dict(entry.options) != merged_options:
        hass.config_entries.async_update_entry(entry, options=merged_options)

    coordinator = SuptronicsUPSCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    entry.async_on_unload(entry.add_update_listener(async_update_options))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        coordinator: SuptronicsUPSCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.async_shutdown()
    return unload_ok


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle config entry options updates."""
    merged_options = merge_options(entry.options)
    if dict(entry.options) != merged_options:
        hass.config_entries.async_update_entry(entry, options=merged_options)
    coordinator: SuptronicsUPSCoordinator = hass.data[DOMAIN][entry.entry_id]
    await coordinator.async_refresh_options()
