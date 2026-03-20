"""Tests for config entry option merging."""

import importlib.util
from pathlib import Path
import sys
import types
import unittest

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_NAME = "custom_components.suptronics_ups_x120x"


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
options_module = _load_module("options", "custom_components/suptronics_ups_x120x/options.py")

merge_options = options_module.merge_options


class TestOptions(unittest.TestCase):
    def test_merge_options_fills_defaults_for_old_entries(self) -> None:
        merged = merge_options({"auto_charge": False})

        self.assertEqual(merged["auto_charge"], False)
        self.assertEqual(
            merged["stop_charge_percent"],
            const.DEFAULT_STOP_CHARGE_PERCENT,
        )
        self.assertEqual(
            merged["resume_charge_percent"],
            const.DEFAULT_RESUME_CHARGE_PERCENT,
        )
        self.assertEqual(merged["invert_ac_power"], const.DEFAULT_INVERT_AC_POWER)


if __name__ == "__main__":
    unittest.main()
