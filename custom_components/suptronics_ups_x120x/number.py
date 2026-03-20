"""Number entities for Suptronics UPS X120x."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_RESUME_CHARGE_PERCENT,
    CONF_STOP_CHARGE_PERCENT,
    DATA_RESUME_THRESHOLD,
    DATA_STOP_THRESHOLD,
    DOMAIN,
)
from .coordinator import SuptronicsUPSCoordinator
from .entity import SuptronicsUPSEntity


@dataclass(frozen=True, kw_only=True)
class SuptronicsNumberDescription(NumberEntityDescription):
    option_key: str
    coordinator_key: str


NUMBERS: tuple[SuptronicsNumberDescription, ...] = (
    SuptronicsNumberDescription(
        key="stop_charge_percent",
        translation_key="stop_charge_percent",
        entity_category=EntityCategory.CONFIG,
        native_min_value=1,
        native_max_value=100,
        native_step=1,
        native_unit_of_measurement=PERCENTAGE,
        option_key=CONF_STOP_CHARGE_PERCENT,
        coordinator_key=DATA_STOP_THRESHOLD,
    ),
    SuptronicsNumberDescription(
        key="resume_charge_percent",
        translation_key="resume_charge_percent",
        entity_category=EntityCategory.CONFIG,
        native_min_value=0,
        native_max_value=99,
        native_step=1,
        native_unit_of_measurement=PERCENTAGE,
        option_key=CONF_RESUME_CHARGE_PERCENT,
        coordinator_key=DATA_RESUME_THRESHOLD,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up configurable numeric entities."""
    coordinator: SuptronicsUPSCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(SuptronicsUPSNumber(coordinator, description) for description in NUMBERS)


class SuptronicsUPSNumber(SuptronicsUPSEntity, NumberEntity):
    """Config-backed number entity."""

    entity_description: SuptronicsNumberDescription

    def __init__(
        self,
        coordinator: SuptronicsUPSCoordinator,
        description: SuptronicsNumberDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{description.key}"

    @property
    def native_value(self) -> float:
        """Return the current configured threshold."""
        return float(self.coordinator.data[self.entity_description.coordinator_key])

    async def async_set_native_value(self, value: float) -> None:
        """Persist the new threshold."""
        new_value = int(value)
        current_options = dict(self._entry.options)
        stop_value = (
            new_value
            if self.entity_description.option_key == CONF_STOP_CHARGE_PERCENT
            else int(current_options[CONF_STOP_CHARGE_PERCENT])
        )
        resume_value = (
            new_value
            if self.entity_description.option_key == CONF_RESUME_CHARGE_PERCENT
            else int(current_options[CONF_RESUME_CHARGE_PERCENT])
        )

        if resume_value >= stop_value:
            raise HomeAssistantError("Resume threshold must be lower than stop threshold")

        current_options[self.entity_description.option_key] = new_value
        self.hass.config_entries.async_update_entry(self._entry, options=current_options)
        await self.coordinator.async_refresh_options()
