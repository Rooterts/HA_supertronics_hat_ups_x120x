"""Hardware access layer for the Suptronics UPS X120x."""

from __future__ import annotations

import logging
from dataclasses import dataclass

import gpiod
import smbus2
from gpiod.line import Direction, Value

from .const import (
    AUTO_ACTION_NONE,
    AUTO_ACTION_RESUMED,
    AUTO_ACTION_STOPPED,
    DATA_AC_POWER,
    DATA_AC_POWER_RAW,
    DATA_BATTERY_PERCENT,
    DATA_BATTERY_PERCENT_RAW,
    DATA_BATTERY_STATE,
    DATA_BATTERY_VOLTAGE,
    DATA_CHARGING_ENABLED,
)

_LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class SuptronicsUPSStatus:
    """Current UPS values."""

    battery_percent: int
    battery_percent_raw: float
    battery_voltage: float
    battery_state: str
    ac_power: bool
    charging_enabled: bool

    def as_dict(self) -> dict[str, int | float | bool | str]:
        """Convert the dataclass to coordinator data."""
        return {
            DATA_BATTERY_PERCENT: self.battery_percent,
            DATA_BATTERY_PERCENT_RAW: round(self.battery_percent_raw, 2),
            DATA_BATTERY_VOLTAGE: round(self.battery_voltage, 3),
            DATA_BATTERY_STATE: self.battery_state,
            DATA_AC_POWER: self.ac_power,
            DATA_CHARGING_ENABLED: self.charging_enabled,
        }


class SuptronicsUPSDevice:
    """Talk to the fuel gauge and GPIO lines used by the X120x boards."""

    def __init__(
        self,
        *,
        i2c_bus: int,
        i2c_address: int,
        gpio_chip: str,
        power_loss_pin: int,
        charge_control_pin: int,
        invert_ac_power: bool,
    ) -> None:
        self._i2c_bus_id = i2c_bus
        self._i2c_address = i2c_address
        self._gpio_chip = gpio_chip
        self._power_loss_pin = power_loss_pin
        self._charge_control_pin = charge_control_pin
        self._invert_ac_power = invert_ac_power
        self._bus: smbus2.SMBus | None = None
        self._gpio_line = None

    def setup(self) -> None:
        """Open the I2C bus."""
        if self._bus is None:
            self._bus = smbus2.SMBus(self._i2c_bus_id)
        if self._gpio_line is None:
            self._gpio_line = gpiod.request_lines(
                self._gpio_chip,
                consumer="ha_suptronics_ups_x120x_charge",
                config={
                    self._charge_control_pin: gpiod.LineSettings(
                        direction=Direction.OUTPUT,
                    )
                },
            )

    def close(self) -> None:
        """Close the I2C bus."""
        if self._bus is not None:
            self._bus.close()
            self._bus = None
        if self._gpio_line is not None:
            self._gpio_line.release()
            self._gpio_line = None

    def read_status(self) -> dict[str, int | float | bool | str]:
        """Read the current UPS status."""
        self.setup()
        voltage = self._read_voltage()
        raw_percent = self._read_capacity()
        ac_gpio_value = self._read_gpio_value(self._power_loss_pin)
        status = SuptronicsUPSStatus(
            battery_percent=max(0, min(100, round(raw_percent))),
            battery_percent_raw=raw_percent,
            battery_voltage=voltage,
            battery_state=self._battery_state(voltage),
            ac_power=self._is_ac_power_present(ac_gpio_value),
            charging_enabled=self.get_charging_enabled(),
        )
        data = status.as_dict()
        data[DATA_AC_POWER_RAW] = self._gpio_value_to_int(ac_gpio_value)
        return data

    def apply_auto_charge_policy(
        self,
        *,
        battery_percent: float,
        ac_power: bool,
        charging_enabled: bool,
        stop_threshold: int,
        resume_threshold: int,
    ) -> str:
        """Apply hysteresis to charging control."""
        if not ac_power:
            return AUTO_ACTION_NONE

        if charging_enabled and battery_percent >= stop_threshold:
            _LOGGER.debug(
                "Stopping charge automatically at %.2f%% (threshold=%s)",
                battery_percent,
                stop_threshold,
            )
            self.set_charging_enabled(False)
            return AUTO_ACTION_STOPPED

        if not charging_enabled and battery_percent <= resume_threshold:
            _LOGGER.debug(
                "Resuming charge automatically at %.2f%% (threshold=%s)",
                battery_percent,
                resume_threshold,
            )
            self.set_charging_enabled(True)
            return AUTO_ACTION_RESUMED

        return AUTO_ACTION_NONE

    def set_charging_enabled(self, enabled: bool) -> None:
        """Control the charge line.

        The manufacturer documents:
        - High on GPIO 16 disables charging
        - Low on GPIO 16 enables charging
        """
        output_value = Value.INACTIVE if enabled else Value.ACTIVE
        self._gpio_line.set_value(self._charge_control_pin, output_value)

    def get_charging_enabled(self) -> bool:
        """Infer the current charge state from the charge control pin."""
        value = self._gpio_line.get_value(self._charge_control_pin)
        return value == Value.INACTIVE

    def _read_voltage(self) -> float:
        raw = self._read_word_data(0x02)
        return raw * 1.25 / 1000 / 16

    def _read_capacity(self) -> float:
        raw = self._read_word_data(0x04)
        return raw / 256

    def _read_word_data(self, register: int) -> int:
        if self._bus is None:
            self.setup()
        assert self._bus is not None
        value = self._bus.read_word_data(self._i2c_address, register)
        return ((value & 0xFF) << 8) | ((value >> 8) & 0xFF)

    def _is_ac_power_present(self, gpio_value: Value) -> bool:
        """Return True when AC power is present.

        The manufacturer PLD script treats GPIO 6 high as AC power OK.
        """
        gpio_high = self._gpio_value_to_int(gpio_value) == 1
        return not gpio_high if self._invert_ac_power else gpio_high

    def _read_gpio_value(self, pin: int) -> Value:
        request = gpiod.request_lines(
            self._gpio_chip,
            consumer="ha_suptronics_ups_x120x_read",
            config={pin: gpiod.LineSettings(direction=Direction.INPUT)},
        )
        try:
            value = request.get_value(pin)
        finally:
            request.release()
        return Value(value)

    @staticmethod
    def _gpio_value_to_int(value: Value) -> int:
        """Convert libgpiod values across versions to a stable 0/1 integer."""
        raw_value = getattr(value, "value", value)

        if raw_value in (0, 1):
            return int(raw_value)

        if isinstance(raw_value, str):
            normalized = raw_value.strip().lower()
            if normalized in {"active", "high", "1"}:
                return 1
            if normalized in {"inactive", "low", "0"}:
                return 0

        if str(value).endswith("ACTIVE"):
            return 1
        if str(value).endswith("INACTIVE"):
            return 0

        raise ValueError(f"Unsupported GPIO value returned by gpiod: {value!r}")

    @staticmethod
    def _battery_state(voltage: float) -> str:
        if voltage >= 3.87:
            return "full"
        if voltage >= 3.70:
            return "high"
        if voltage >= 3.55:
            return "medium"
        if voltage >= 3.40:
            return "low"
        return "critical"
