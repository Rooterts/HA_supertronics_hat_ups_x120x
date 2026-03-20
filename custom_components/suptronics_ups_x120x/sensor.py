"""Sensor entities for Suptronics UPS X120x."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, PERCENTAGE, UnitOfElectricPotential
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DATA_BATTERY_PERCENT,
    DATA_BATTERY_PERCENT_RAW,
    DATA_BATTERY_STATE,
    DATA_BATTERY_VOLTAGE,
    DOMAIN,
)
from .coordinator import SuptronicsUPSCoordinator
from .entity import SuptronicsUPSEntity


@dataclass(frozen=True, kw_only=True)
class SuptronicsSensorDescription(SensorEntityDescription):
    value_fn: Callable[[dict[str, Any]], Any]


SENSORS: tuple[SuptronicsSensorDescription, ...] = (
    SuptronicsSensorDescription(
        key="battery_percent",
        translation_key="battery_percent",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        value_fn=lambda data: data[DATA_BATTERY_PERCENT],
    ),
    SuptronicsSensorDescription(
        key="battery_voltage",
        translation_key="battery_voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        suggested_display_precision=3,
        value_fn=lambda data: data[DATA_BATTERY_VOLTAGE],
    ),
    SuptronicsSensorDescription(
        key="battery_state",
        translation_key="battery_state",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data[DATA_BATTERY_STATE],
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor entities."""
    coordinator: SuptronicsUPSCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(SuptronicsUPSSensor(coordinator, description) for description in SENSORS)


class SuptronicsUPSSensor(SuptronicsUPSEntity, SensorEntity):
    """Coordinator-backed UPS sensor."""

    entity_description: SuptronicsSensorDescription

    def __init__(
        self,
        coordinator: SuptronicsUPSCoordinator,
        description: SuptronicsSensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{description.key}"

    @property
    def native_value(self) -> Any:
        """Return the sensor value."""
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return extra state attributes."""
        if self.entity_description.key != "battery_percent":
            return None
        return {"raw_percentage": self.coordinator.data[DATA_BATTERY_PERCENT_RAW]}
