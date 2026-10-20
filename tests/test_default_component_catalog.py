
"""Tests del catálogo comercial inicial de Helios."""

import pytest

from helios.solar.components_catalog import ComponentCatalog
from helios.solar.default_component_catalog import (
    build_default_component_catalog,
)


def test_default_catalog_returns_component_catalog():
    catalog = build_default_component_catalog()

    assert isinstance(catalog, ComponentCatalog)


def test_default_catalog_contains_identified_panel():
    catalog = build_default_component_catalog()

    assert len(catalog.panels) == 1

    panel = catalog.get_panel("longi lr7-60hvh-540m")

    assert panel.manufacturer == "Longi"
    assert panel.model == "LR7-60HVH-540M"
    assert panel.power_wp == pytest.approx(540.0)
    assert panel.price_eur == pytest.approx(92.196)
    assert panel.area_m2 == pytest.approx(1.134 * 1.990)


def test_default_catalog_contains_identified_hybrid_inverter():
    catalog = build_default_component_catalog()

    assert len(catalog.inverters) == 1

    inverter = catalog.get_inverter("goodwe-gw8k-eha-g20")

    assert inverter.manufacturer == "GoodWe"
    assert inverter.model == "GW8K-EHA-G20"
    assert inverter.nominal_power_kw == pytest.approx(8.0)
    assert inverter.price_eur == pytest.approx(960.38)
    assert inverter.hybrid is True


def test_default_catalog_contains_identified_auxiliary_costs():
    catalog = build_default_component_catalog()

    costs = {
        item.id: item
        for item in catalog.auxiliary_costs
    }

    expected_costs = {
        "electrical_protection": 343.96,
        "solar_cabling": 110.58,
        "connector_female": 14.78,
        "connector_male": 14.18,
        "joining_profiles": 8.27,
        "installation": 2950.0,
        "legalization_estimate": 650.0,
    }

    assert set(costs) == set(expected_costs)

    for cost_id, expected_price in expected_costs.items():
        assert costs[cost_id].unit_price_eur == pytest.approx(
            expected_price
        )
        assert costs[cost_id].basis == "fixed"


def test_default_catalog_does_not_invent_battery_or_mounting_prices():
    catalog = build_default_component_catalog()

    assert catalog.batteries == ()
    assert catalog.mounting_systems == ()
    assert catalog.mounting_packages == ()


def test_default_catalog_uses_unique_identifiers():
    catalog = build_default_component_catalog()

    identifiers = [
        item.id
        for collection in (
            catalog.panels,
            catalog.inverters,
            catalog.batteries,
            catalog.mounting_systems,
            catalog.auxiliary_costs,
            catalog.mounting_packages,
        )
        for item in collection
    ]

    assert len(identifiers) == len(set(identifiers))
