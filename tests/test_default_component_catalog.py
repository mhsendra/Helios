
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
    assert inverter.price_eur == pytest.approx(960.375)
    assert inverter.hybrid is True

def test_default_catalog_contains_identified_auxiliary_costs():
    catalog = build_default_component_catalog()

    costs = {
        item.id: item
        for item in catalog.auxiliary_costs
    }

    expected_costs = {
        "electrical_protection_dc": 241.53,
        "electrical_protection_ac": 102.432,
        "solar_cabling_red": 1.1058,
        "solar_cabling_black": 1.1058,
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

    assert costs["electrical_protection_dc"].basis == "fixed"
    assert costs["electrical_protection_ac"].basis == "fixed"

    for cost_id in ("solar_cabling_red", "solar_cabling_black"):
        assert costs[cost_id].basis == "per_metre"
        assert costs[cost_id].quantity == pytest.approx(50.0)

    for cost_id in (
        "connector_female",
        "connector_male",
        "joining_profiles",
        "installation",
        "legalization_estimate",
    ):
        assert costs[cost_id].basis == "fixed"

def test_default_catalog_keeps_battery_price_unknown_and_uses_only_confirmed_mounting_quote():
    catalog = build_default_component_catalog()

    assert catalog.batteries == ()
    assert len(catalog.mounting_systems) == 1
    assert catalog.get_mounting_system("mounting-arabic-tile").price_per_panel_eur is None
    assert len(catalog.mounting_packages) == 2

    selection_packages = {
        package.id: package
        for package in catalog.mounting_packages
    }
    assert selection_packages["mounting-arabic-tile-3-panel"].total_price_eur == pytest.approx(291.00)
    assert selection_packages["mounting-arabic-tile-2-panel"].total_price_eur == pytest.approx(101.27)
    assert sum(package.total_price_eur for package in catalog.mounting_packages) == pytest.approx(392.27)
    assert sum(package.total_panel_capacity for package in catalog.mounting_packages) == 16


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

def test_default_catalog_calculates_net_prices_from_list_prices():
    catalog = build_default_component_catalog()

    panel = catalog.get_panel("longi lr7-60hvh-540m")
    inverter = catalog.get_inverter("goodwe-gw8k-eha-g20")

    assert panel.list_price_eur == pytest.approx(156.00)
    assert panel.price_eur == pytest.approx(92.196)
    assert panel.discount_1_percent == pytest.approx(40.0)
    assert panel.discount_2_percent == pytest.approx(1.5)
    assert panel.area_m2 == pytest.approx(1.134 * 1.990)

    assert inverter.list_price_eur == pytest.approx(1625.00)
    assert inverter.price_eur == pytest.approx(960.375)
    assert inverter.discount_1_percent == pytest.approx(40.0)
    assert inverter.discount_2_percent == pytest.approx(1.5)

def test_default_catalog_contains_cables_and_does_not_extrapolate_mounting_prices():
    catalog = build_default_component_catalog()

    costs = {
        item.id: item
        for item in catalog.auxiliary_costs
    }

    assert catalog.get_mounting_system("mounting-arabic-tile").price_per_panel_eur is None
    assert len(catalog.mounting_packages) == 2

    red_cable = costs["solar_cabling_red"]
    black_cable = costs["solar_cabling_black"]

    for cable in (red_cable, black_cable):
        assert cable.basis == "per_metre"
        assert cable.quantity == pytest.approx(50.0)
        assert cable.list_price_eur == pytest.approx(1.90)
        assert cable.unit_price_eur == pytest.approx(1.1058)

    assert (
        red_cable.unit_price_eur * red_cable.quantity
        + black_cable.unit_price_eur * black_cable.quantity
    ) == pytest.approx(110.58)