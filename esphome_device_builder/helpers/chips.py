"""Chip-vocabulary helpers importable without the models package.

The validate-definitions pre-commit hook runs without the package's
dependencies installed, so this module must stay import-light (stdlib only).
"""

from __future__ import annotations

import re


def normalize_chip_variant(name: str) -> str:
    """Fold a chip-variant spelling (``ESP32-C3`` / ``esp32_c3``) onto the catalog form."""
    return name.strip().replace("-", "").replace("_", "").lower()


_NRF52_PORT_PIN = re.compile(r"P([01])\.(\d{1,2})")


def parse_manifest_gpio(value: int | str) -> int:
    """Return the GPIO number for a manifest ``gpio`` (an int, or nRF52 ``P<port>.<pin>``)."""
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    if isinstance(value, str) and (match := _NRF52_PORT_PIN.fullmatch(value.strip())):
        port, pin = int(match[1]), int(match[2])
        if pin < 32:
            return port * 32 + pin
    raise ValueError(f"invalid gpio {value!r}")


# ESPHome's LibreTiny board meta and the YAML's ``family:`` name the chip.
# Fold it into the per-chip series token (``mcu``): BK7231N/T/Q share one
# ``bk7231``, the rest map 1:1.
_LIBRETINY_FAMILY_MCU: dict[str, str] = {
    "BK7231N": "bk7231",
    "BK7231T": "bk7231",
    "BK7231Q": "bk7231",
}


def libretiny_family_mcu(family: str) -> str:
    """
    Fold a LibreTiny family (``RTL8720C``) onto its chip series token.

    A family outside the fold is its own lowercased token, so a new chip
    gets a distinct one the day ESPHome lists it.
    """
    folded = family.strip().upper()
    return _LIBRETINY_FAMILY_MCU.get(folded) or normalize_chip_variant(folded)
