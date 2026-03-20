"""Coordinator for the Suptronics UPS X120x integration."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    AUTO_ACTION_NONE,
    CONF_AUTO_CHARGE,
    CONF_CHARGE_CONTROL_PIN,
    CONF_GPIO_CHIP,
    CONF_I2C_ADDRESS,
    CONF_I2C_BUS,
    CONF_POWER_LOSS_PIN,
    CONF_RESUME_CHARGE_PERCENT,
    CONF_SCAN_INTERVAL,
    CONF_STOP_CHARGE_PERCENT,
    DEFAULT_AUTO_CHARGE,
    DEFAULT_CHARGE_CONTROL_PIN,
    DEFAULT_GPIO_CHIP,
    DEFAULT_I2C_ADDRESS,
    DEFAULT_I2C_BUS,
    DEFAULT_POWER_LOSS_PIN,
    DEFAULT_RESUME_CHARGE_PERCENT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_STOP_CHARGE_PERCENT,
    DATA_AUTO_CHARGE,
    DATA_AC_POWER,
    DATA_BATTERY_PERCENT_RAW,
    DATA_CHARGING_ENABLED,
    DATA_LAST_AUTO_ACTION,
    DATA_RESUME_THRESHOLD,
    DATA_STOP_THRESHOLD,
    DOMAIN,
)
from .device import SuptronicsUPSDevice

_LOGGER = logging.getLogger(__name__)


class SuptronicsUPSCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Central polling coordinator."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        self.config_entry = config_entry
        self.device = SuptronicsUPSDevice(
            i2c_bus=config_entry.options.get(CONF_I2C_BUS, DEFAULT_I2C_BUS),
            i2c_address=config_entry.options.get(CONF_I2C_ADDRESS, DEFAULT_I2C_ADDRESS),
            gpio_chip=config_entry.options.get(CONF_GPIO_CHIP, DEFAULT_GPIO_CHIP),
            power_loss_pin=config_entry.options.get(CONF_POWER_LOSS_PIN, DEFAULT_POWER_LOSS_PIN),
            charge_control_pin=config_entry.options.get(
                CONF_CHARGE_CONTROL_PIN, DEFAULT_CHARGE_CONTROL_PIN
            ),
        )
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(
                seconds=config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
            ),
        )

    async def async_config_entry_first_refresh(self) -> None:
        """Open hardware before the first update."""
        try:
            await self.hass.async_add_executor_job(self.device.setup)
        except OSError as err:
            raise ConfigEntryNotReady(f"Unable to access UPS hardware: {err}") from err

        await super().async_config_entry_first_refresh()

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data and apply charge policy."""
        try:
            data = await self.hass.async_add_executor_job(self.device.read_status)
            last_action = AUTO_ACTION_NONE
            auto_charge = self.config_entry.options.get(CONF_AUTO_CHARGE, DEFAULT_AUTO_CHARGE)
            stop_threshold = self.config_entry.options.get(
                CONF_STOP_CHARGE_PERCENT, DEFAULT_STOP_CHARGE_PERCENT
            )
            resume_threshold = self.config_entry.options.get(
                CONF_RESUME_CHARGE_PERCENT, DEFAULT_RESUME_CHARGE_PERCENT
            )

            if auto_charge:
                last_action = await self.hass.async_add_executor_job(
                    lambda: self.device.apply_auto_charge_policy(
                        battery_percent=float(data[DATA_BATTERY_PERCENT_RAW]),
                        ac_power=bool(data[DATA_AC_POWER]),
                        charging_enabled=bool(data[DATA_CHARGING_ENABLED]),
                        stop_threshold=stop_threshold,
                        resume_threshold=resume_threshold,
                    )
                )
                if last_action != AUTO_ACTION_NONE:
                    data = await self.hass.async_add_executor_job(self.device.read_status)

            data[DATA_AUTO_CHARGE] = auto_charge
            data[DATA_STOP_THRESHOLD] = stop_threshold
            data[DATA_RESUME_THRESHOLD] = resume_threshold
            data[DATA_LAST_AUTO_ACTION] = last_action
            return data
        except OSError as err:
            raise UpdateFailed(f"Failed to update UPS data: {err}") from err

    async def async_refresh_options(self) -> None:
        """Reapply polling interval after options changes."""
        self.update_interval = timedelta(
            seconds=self.config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        )
        await self.async_request_refresh()

    async def async_shutdown(self) -> None:
        """Release hardware resources."""
        await self.hass.async_add_executor_job(self.device.close)
