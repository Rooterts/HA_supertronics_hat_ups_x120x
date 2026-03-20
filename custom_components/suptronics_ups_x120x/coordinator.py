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
    CONF_INVERT_AC_POWER,
    CONF_POWER_LOSS_PIN,
    CONF_RESUME_CHARGE_PERCENT,
    CONF_SCAN_INTERVAL,
    CONF_STOP_CHARGE_PERCENT,
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
from .options import merge_options

_LOGGER = logging.getLogger(__name__)


class SuptronicsUPSCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Central polling coordinator."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        self.config_entry = config_entry
        options = merge_options(config_entry.options)
        self.device = SuptronicsUPSDevice(
            i2c_bus=int(options[CONF_I2C_BUS]),
            i2c_address=int(options[CONF_I2C_ADDRESS]),
            gpio_chip=str(options[CONF_GPIO_CHIP]),
            power_loss_pin=int(options[CONF_POWER_LOSS_PIN]),
            charge_control_pin=int(options[CONF_CHARGE_CONTROL_PIN]),
            invert_ac_power=bool(options[CONF_INVERT_AC_POWER]),
        )
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=int(options[CONF_SCAN_INTERVAL])),
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
            options = merge_options(self.config_entry.options)
            auto_charge = bool(options[CONF_AUTO_CHARGE])
            stop_threshold = int(options[CONF_STOP_CHARGE_PERCENT])
            resume_threshold = int(options[CONF_RESUME_CHARGE_PERCENT])

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
        options = merge_options(self.config_entry.options)
        self.update_interval = timedelta(seconds=int(options[CONF_SCAN_INTERVAL]))
        await self.async_request_refresh()

    async def async_shutdown(self) -> None:
        """Release hardware resources."""
        await self.hass.async_add_executor_job(self.device.close)
