"""Config flow for Suptronics UPS X120x."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
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
    DEFAULT_AUTO_CHARGE,
    DEFAULT_CHARGE_CONTROL_PIN,
    DEFAULT_GPIO_CHIP,
    DEFAULT_I2C_ADDRESS,
    DEFAULT_I2C_BUS,
    DEFAULT_INVERT_AC_POWER,
    DEFAULT_POWER_LOSS_PIN,
    DEFAULT_RESUME_CHARGE_PERCENT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_STOP_CHARGE_PERCENT,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
)
from .validators import validate_thresholds


class SuptronicsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the initial setup flow."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None):
        """Create the single config entry."""
        errors: dict[str, str] = {}
        if user_input is not None:
            errors = validate_thresholds(
                user_input[CONF_STOP_CHARGE_PERCENT],
                user_input[CONF_RESUME_CHARGE_PERCENT],
            )
            if not errors:
                await self.async_set_unique_id(DOMAIN)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title="HA Supertronics HAT UPS X120x",
                    data={},
                    options=user_input,
                )

        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()
        return self.async_show_form(
            step_id="user",
            data_schema=_options_schema(user_input),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> SuptronicsOptionsFlow:
        """Create the options flow."""
        return SuptronicsOptionsFlow()


class SuptronicsOptionsFlow(config_entries.OptionsFlow):
    """Handle options updates."""

    async def async_step_init(self, user_input: dict | None = None):
        """Manage options."""
        errors: dict[str, str] = {}
        if user_input is not None:
            errors = validate_thresholds(
                user_input[CONF_STOP_CHARGE_PERCENT],
                user_input[CONF_RESUME_CHARGE_PERCENT],
            )
            if not errors:
                return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=_options_schema(self.config_entry.options),
            errors=errors,
        )

def _options_schema(options: dict | None = None) -> vol.Schema:
    options = options or {}
    return vol.Schema(
        {
            vol.Required(
                CONF_AUTO_CHARGE,
                default=options.get(CONF_AUTO_CHARGE, DEFAULT_AUTO_CHARGE),
            ): bool,
            vol.Required(
                CONF_STOP_CHARGE_PERCENT,
                default=options.get(CONF_STOP_CHARGE_PERCENT, DEFAULT_STOP_CHARGE_PERCENT),
            ): vol.All(vol.Coerce(int), vol.Range(min=1, max=100)),
            vol.Required(
                CONF_RESUME_CHARGE_PERCENT,
                default=options.get(CONF_RESUME_CHARGE_PERCENT, DEFAULT_RESUME_CHARGE_PERCENT),
            ): vol.All(vol.Coerce(int), vol.Range(min=0, max=99)),
            vol.Required(
                CONF_SCAN_INTERVAL,
                default=options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
            ): vol.All(vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL)),
            vol.Required(
                CONF_GPIO_CHIP,
                default=options.get(CONF_GPIO_CHIP, DEFAULT_GPIO_CHIP),
            ): str,
            vol.Required(
                CONF_I2C_BUS,
                default=options.get(CONF_I2C_BUS, DEFAULT_I2C_BUS),
            ): vol.All(vol.Coerce(int), vol.Range(min=0, max=32)),
            vol.Required(
                CONF_I2C_ADDRESS,
                default=options.get(CONF_I2C_ADDRESS, DEFAULT_I2C_ADDRESS),
            ): vol.All(vol.Coerce(int), vol.Range(min=0x03, max=0x77)),
            vol.Required(
                CONF_POWER_LOSS_PIN,
                default=options.get(CONF_POWER_LOSS_PIN, DEFAULT_POWER_LOSS_PIN),
            ): vol.All(vol.Coerce(int), vol.Range(min=0, max=64)),
            vol.Required(
                CONF_CHARGE_CONTROL_PIN,
                default=options.get(CONF_CHARGE_CONTROL_PIN, DEFAULT_CHARGE_CONTROL_PIN),
            ): vol.All(vol.Coerce(int), vol.Range(min=0, max=64)),
            vol.Required(
                CONF_INVERT_AC_POWER,
                default=options.get(CONF_INVERT_AC_POWER, DEFAULT_INVERT_AC_POWER),
            ): bool,
        }
    )
