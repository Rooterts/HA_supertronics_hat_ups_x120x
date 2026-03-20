"""Switch entities for Suptronics UPS X120x."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_AUTO_CHARGE, DATA_AUTO_CHARGE, DATA_CHARGING_ENABLED, DOMAIN
from .coordinator import SuptronicsUPSCoordinator
from .entity import SuptronicsUPSEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up UPS switch entities."""
    coordinator: SuptronicsUPSCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            SuptronicsChargingSwitch(
                coordinator,
                SwitchEntityDescription(
                    key="charging",
                    translation_key="charging",
                ),
            ),
            SuptronicsAutomaticChargingSwitch(
                coordinator,
                SwitchEntityDescription(
                    key="automatic_charging",
                    translation_key="automatic_charging",
                ),
            ),
        ]
    )


class SuptronicsChargingSwitch(SuptronicsUPSEntity, SwitchEntity):
    """Manual charging control."""

    def __init__(
        self,
        coordinator: SuptronicsUPSCoordinator,
        description: SwitchEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{description.key}"

    @property
    def is_on(self) -> bool:
        """Return the inferred charge state."""
        return bool(self.coordinator.data[DATA_CHARGING_ENABLED])

    async def async_turn_on(self, **kwargs) -> None:
        """Enable charging."""
        await self.hass.async_add_executor_job(
            self.coordinator.device.set_charging_enabled,
            True,
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Disable charging."""
        await self.hass.async_add_executor_job(
            self.coordinator.device.set_charging_enabled,
            False,
        )
        await self.coordinator.async_request_refresh()


class SuptronicsAutomaticChargingSwitch(SuptronicsUPSEntity, SwitchEntity):
    """Enable or disable the automatic charging policy."""

    def __init__(
        self,
        coordinator: SuptronicsUPSCoordinator,
        description: SwitchEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{description.key}"

    @property
    def is_on(self) -> bool:
        """Return whether automatic charge control is enabled."""
        return bool(self.coordinator.data[DATA_AUTO_CHARGE])

    async def async_turn_on(self, **kwargs) -> None:
        """Enable the automatic charge policy."""
        self.hass.config_entries.async_update_entry(
            self._entry,
            options={**self._entry.options, CONF_AUTO_CHARGE: True},
        )
        await self.coordinator.async_refresh_options()

    async def async_turn_off(self, **kwargs) -> None:
        """Disable the automatic charge policy."""
        self.hass.config_entries.async_update_entry(
            self._entry,
            options={**self._entry.options, CONF_AUTO_CHARGE: False},
        )
        await self.coordinator.async_refresh_options()
