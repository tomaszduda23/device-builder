"""Manifest ``gpio`` parsing: integers and the nRF52 ``P<port>.<pin>`` form."""

from __future__ import annotations

from pathlib import Path

import pytest

import script.validate_definitions as vd
from esphome_device_builder.definitions import _load_pin
from esphome_device_builder.helpers.chips import parse_manifest_gpio


@pytest.mark.parametrize(
    ("raw", "expected"),
    [(0, 0), (47, 47), ("P0.0", 0), ("P0.2", 2), ("P0.31", 31), ("P1.0", 32), ("P1.7", 39)],
)
def test_parse_manifest_gpio(raw: int | str, expected: int) -> None:
    assert parse_manifest_gpio(raw) == expected


@pytest.mark.parametrize("raw", ["P2.0", "P0.32", "GPIO2", "2", True, None])
def test_parse_manifest_gpio_rejects(raw: object) -> None:
    with pytest.raises(ValueError, match="invalid gpio"):
        parse_manifest_gpio(raw)  # type: ignore[arg-type]


def test_load_pin_stores_port_pin_as_int() -> None:
    pin = _load_pin({"gpio": "P1.5", "label": "P1.5"}, "b")
    assert pin.gpio == 37


def _board(platform: str, board: str, pins: list[dict]) -> dict:
    return {
        "id": "b",
        "name": "B",
        "description": "",
        "manufacturer": "",
        "esphome": {"platform": platform, "board": board},
        "pins": pins,
    }


def test_validate_accepts_port_pin_on_nrf52() -> None:
    data = _board("nrf52", "xiao_ble", [{"gpio": "P0.2"}, {"gpio": "P1.7"}])
    assert vd.validate_board(Path("boards/b/manifest.yaml"), data=data) == []


def test_validate_rejects_port_pin_off_nrf52() -> None:
    data = _board("esp32", "esp32dev", [{"gpio": "P0.2"}])
    data["esphome"]["variant"] = "esp32"
    errors = vd.validate_board(Path("boards/b/manifest.yaml"), data=data)
    assert errors == ["b: gpio 'P0.2' — port.pin form is nrf52-only"]


def test_validate_flags_duplicate_across_forms() -> None:
    data = _board("nrf52", "xiao_ble", [{"gpio": "P1.7"}, {"gpio": 39}])
    errors = vd.validate_board(Path("boards/b/manifest.yaml"), data=data)
    assert errors == ["b: duplicate gpio 39"]
