"""Constants for the Suptronics UPS X120x integration."""

from __future__ import annotations

DOMAIN = "suptronics_ups_x120x"
NAME = "Suptronics UPS X120x"

CONF_AUTO_CHARGE = "auto_charge"
CONF_STOP_CHARGE_PERCENT = "stop_charge_percent"
CONF_RESUME_CHARGE_PERCENT = "resume_charge_percent"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_GPIO_CHIP = "gpio_chip"
CONF_I2C_BUS = "i2c_bus"
CONF_I2C_ADDRESS = "i2c_address"
CONF_POWER_LOSS_PIN = "power_loss_pin"
CONF_CHARGE_CONTROL_PIN = "charge_control_pin"

DEFAULT_AUTO_CHARGE = True
DEFAULT_STOP_CHARGE_PERCENT = 100
DEFAULT_RESUME_CHARGE_PERCENT = 95
DEFAULT_SCAN_INTERVAL = 30
DEFAULT_GPIO_CHIP = "/dev/gpiochip0"
DEFAULT_I2C_BUS = 1
DEFAULT_I2C_ADDRESS = 0x36
DEFAULT_POWER_LOSS_PIN = 6
DEFAULT_CHARGE_CONTROL_PIN = 16

MIN_SCAN_INTERVAL = 5
MAX_SCAN_INTERVAL = 3600

DATA_BATTERY_PERCENT = "battery_percent"
DATA_BATTERY_PERCENT_RAW = "battery_percent_raw"
DATA_BATTERY_VOLTAGE = "battery_voltage"
DATA_BATTERY_STATE = "battery_state"
DATA_AC_POWER = "ac_power"
DATA_CHARGING_ENABLED = "charging_enabled"
DATA_AUTO_CHARGE = "auto_charge"
DATA_STOP_THRESHOLD = "stop_threshold"
DATA_RESUME_THRESHOLD = "resume_threshold"
DATA_LAST_AUTO_ACTION = "last_auto_action"

AUTO_ACTION_NONE = "none"
AUTO_ACTION_STOPPED = "stopped_charging"
AUTO_ACTION_RESUMED = "resumed_charging"
