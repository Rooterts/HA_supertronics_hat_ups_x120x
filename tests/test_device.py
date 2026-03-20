"""Basic tests for UPS hardware policy logic."""

import importlib.util
from pathlib import Path
import sys
import types
import unittest

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_NAME = "custom_components.suptronics_ups_x120x"


fake_gpiod = types.ModuleType("gpiod")
fake_gpiod.request_lines = lambda *args, **kwargs: None
fake_gpiod.LineSettings = object

fake_gpiod_line = types.ModuleType("gpiod.line")


class _FakeDirection:
    OUTPUT = "output"
    INPUT = "input"


class _FakeValue(int):
    ACTIVE = 1
    INACTIVE = 0


fake_gpiod_line.Direction = _FakeDirection
fake_gpiod_line.Value = _FakeValue

fake_smbus2 = types.ModuleType("smbus2")
fake_smbus2.SMBus = object

sys.modules.setdefault("gpiod", fake_gpiod)
sys.modules.setdefault("gpiod.line", fake_gpiod_line)
sys.modules.setdefault("smbus2", fake_smbus2)


def _ensure_package() -> None:
    custom_components_pkg = sys.modules.setdefault(
        "custom_components",
        types.ModuleType("custom_components"),
    )
    if not hasattr(custom_components_pkg, "__path__"):
        custom_components_pkg.__path__ = [str(ROOT / "custom_components")]

    integration_pkg = sys.modules.setdefault(PACKAGE_NAME, types.ModuleType(PACKAGE_NAME))
    if not hasattr(integration_pkg, "__path__"):
        integration_pkg.__path__ = [str(ROOT / "custom_components" / "suptronics_ups_x120x")]


def _load_module(module_name: str, relative_path: str):
    _ensure_package()
    full_name = f"{PACKAGE_NAME}.{module_name}"
    spec = importlib.util.spec_from_file_location(full_name, ROOT / relative_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[full_name] = module
    spec.loader.exec_module(module)
    return module


const = _load_module("const", "custom_components/suptronics_ups_x120x/const.py")
device_module = _load_module("device", "custom_components/suptronics_ups_x120x/device.py")

AUTO_ACTION_NONE = const.AUTO_ACTION_NONE
AUTO_ACTION_RESUMED = const.AUTO_ACTION_RESUMED
AUTO_ACTION_STOPPED = const.AUTO_ACTION_STOPPED
SuptronicsUPSDevice = device_module.SuptronicsUPSDevice


class DummyDevice(SuptronicsUPSDevice):
    """Minimal test double that records charge commands."""

    def __init__(self) -> None:
        super().__init__(
            i2c_bus=1,
            i2c_address=0x36,
            gpio_chip="/dev/gpiochip0",
            power_loss_pin=6,
            charge_control_pin=16,
            invert_ac_power=False,
        )
        self.commands: list[bool] = []

    def set_charging_enabled(self, enabled: bool) -> None:
        self.commands.append(enabled)


class TestDevicePolicy(unittest.TestCase):
    def test_auto_charge_stops_at_threshold(self) -> None:
        device = DummyDevice()

        result = device.apply_auto_charge_policy(
            battery_percent=100.0,
            ac_power=True,
            charging_enabled=True,
            stop_threshold=100,
            resume_threshold=95,
        )

        self.assertEqual(result, AUTO_ACTION_STOPPED)
        self.assertEqual(device.commands, [False])

    def test_auto_charge_resumes_below_resume_threshold(self) -> None:
        device = DummyDevice()

        result = device.apply_auto_charge_policy(
            battery_percent=94.5,
            ac_power=True,
            charging_enabled=False,
            stop_threshold=100,
            resume_threshold=95,
        )

        self.assertEqual(result, AUTO_ACTION_RESUMED)
        self.assertEqual(device.commands, [True])

    def test_auto_charge_does_nothing_without_ac_power(self) -> None:
        device = DummyDevice()

        result = device.apply_auto_charge_policy(
            battery_percent=100.0,
            ac_power=False,
            charging_enabled=True,
            stop_threshold=100,
            resume_threshold=95,
        )

        self.assertEqual(result, AUTO_ACTION_NONE)
        self.assertEqual(device.commands, [])


if __name__ == "__main__":
    unittest.main()
