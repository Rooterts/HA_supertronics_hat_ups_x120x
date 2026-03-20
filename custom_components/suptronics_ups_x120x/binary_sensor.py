"""Binary sensor entities for Suptronics UPS X120x."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DATA_AC_POWER, DOMAIN
from .coordinator import SuptronicsUPSCoordinator
from .entity import SuptronicsUPSEntity

AC_POWER_SENSOR = BinarySensorEntityDescription(
    key="ac_power",
    translation_key="ac_power",
    device_class=BinarySensorDeviceClass.POWER,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up binary sensor entities."""
    coordinator: SuptronicsUPSCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SuptronicsACPowerBinarySensor(coordinator)])


class SuptronicsACPowerBinarySensor(SuptronicsUPSEntity, BinarySensorEntity):
    """Expose AC presence from the manufacturer PLD pin."""

    entity_description = AC_POWER_SENSOR

    def __init__(self, coordinator: SuptronicsUPSCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_ac_power"

    @property
    def is_on(self) -> bool:
        """Return True when AC power is present."""
        return bool(self.coordinator.data[DATA_AC_POWER])
