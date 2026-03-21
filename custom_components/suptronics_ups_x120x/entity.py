"""Shared entity base for the Suptronics UPS X120x integration."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SuptronicsUPSCoordinator


class SuptronicsUPSEntity(CoordinatorEntity[SuptronicsUPSCoordinator]):
    """Common entity behavior."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: SuptronicsUPSCoordinator) -> None:
        super().__init__(coordinator)
        self._entry = coordinator.config_entry

    @property
    def device_info(self) -> DeviceInfo:
        """Return the parent device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            manufacturer="SupTronics",
            model="X1200/X1201/X1202",
            name="HA Supertronics HAT UPS X120x",
        )
