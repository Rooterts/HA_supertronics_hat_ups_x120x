"""Tests for standalone validation helpers."""

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


validate_thresholds = _load_module(
    "validators",
    "custom_components/suptronics_ups_x120x/validators.py",
).validate_thresholds


class TestValidation(unittest.TestCase):
    def test_thresholds_valid_when_resume_is_lower(self) -> None:
        self.assertEqual(validate_thresholds(100, 95), {})

    def test_thresholds_invalid_when_resume_matches_stop(self) -> None:
        self.assertEqual(
            validate_thresholds(100, 100),
            {"base": "resume_must_be_lower"},
        )


if __name__ == "__main__":
    unittest.main()
