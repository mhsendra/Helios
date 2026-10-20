import pytest

from dataclasses import replace

from helios.solar.components_catalog import (
    AuxiliaryCostItem,
    BatteryProduct,
    ComponentCatalog,
    Inverter,
    MountingSystem,
    PhotovoltaicPanel,
    MountingSystemPackage,
)

@pytest.fixture
def panel():
    return PhotovoltaicPanel(
        id="panel-540",
        manufacturer="Fabricante A",
        model="Panel 540",
        power_wp=540.0,
        width_m=1.134,
        height_m=2.278,
        price_eur=92.196,
    )


@pytest.fixture
def hybrid_inverter():
    return Inverter(
        id="inverter-hybrid-8",
        manufacturer="Fabricante B",
        model="Híbrido 8 kW",
        nominal_power_kw=8.0,
        max_pv_power_kwp=12.0,
        price_eur=1500.0,
        hybrid=True,
    )


@pytest.fixture
def battery(hybrid_inverter):
    return BatteryProduct(
        id="battery-8",
        manufacturer="Fabricante C",
        model="Batería 8 kWh",
        capacity_kwh=8.0,
        max_charge_power_kw=5.0,
        max_discharge_power_kw=5.0,
        price_eur=249.70 * 8.0,
        compatible_inverter_ids=(hybrid_inverter.id,),
    )


def test_panel_calculates_area(panel):
    assert panel.area_m2 == pytest.approx(1.134 * 2.278)


def test_panel_accepts_configurable_price(panel):
    assert panel.price_eur == pytest.approx(92.196)


@pytest.mark.parametrize(
    "field,value",
    [
        ("id", ""),
        ("manufacturer", ""),
        ("model", ""),
        ("technology", ""),
    ],
)
def test_panel_rejects_empty_text(field, value):
    values = {
        "id": "panel-540",
        "manufacturer": "Fabricante A",
        "model": "Panel 540",
        "power_wp": 540.0,
        "width_m": 1.134,
        "height_m": 2.278,
        "price_eur": 100.0,
        "technology": "monocrystalline",
    }
    values[field] = value

    with pytest.raises(ValueError, match="cannot be empty"):
        PhotovoltaicPanel(**values)


@pytest.mark.parametrize(
    "field,value,error_message",
    [
        ("power_wp", 0, "greater than zero"),
        ("power_wp", -540, "cannot be negative"),
        ("width_m", 0, "greater than zero"),
        ("height_m", -1, "cannot be negative"),
    ],
)
def test_panel_rejects_non_positive_dimensions_or_power(
    field,
    value,
    error_message,
):
    values = {
        "id": "panel-540",
        "manufacturer": "Fabricante A",
        "model": "Panel 540",
        "power_wp": 540.0,
        "width_m": 1.134,
        "height_m": 2.278,
        "price_eur": 100.0,
    }
    values[field] = value

    with pytest.raises(ValueError, match=error_message):
        PhotovoltaicPanel(**values)

@pytest.mark.parametrize("price", [-1.0, float("nan"), float("inf")])
def test_panel_rejects_invalid_price(price):
    with pytest.raises(ValueError):
        PhotovoltaicPanel(
            id="panel-540",
            manufacturer="Fabricante A",
            model="Panel 540",
            power_wp=540.0,
            width_m=1.134,
            height_m=2.278,
            price_eur=price,
        )


def test_inverter_accepts_configurable_specifications(hybrid_inverter):
    assert hybrid_inverter.nominal_power_kw == 8.0
    assert hybrid_inverter.max_pv_power_kwp == 12.0
    assert hybrid_inverter.hybrid is True


def test_battery_is_compatible_with_declared_inverter(
    battery,
    hybrid_inverter,
):
    assert battery.is_compatible_with(hybrid_inverter)


def test_battery_is_not_compatible_with_undeclared_inverter(battery):
    other_inverter = Inverter(
        id="inverter-other",
        manufacturer="Fabricante D",
        model="Inversor no compatible",
        nominal_power_kw=5.0,
        max_pv_power_kwp=7.5,
        price_eur=900.0,
        hybrid=True,
    )

    assert not battery.is_compatible_with(other_inverter)


def test_battery_rejects_invalid_soc_limits(hybrid_inverter):
    with pytest.raises(ValueError, match="SOC limits"):
        BatteryProduct(
            id="battery-invalid",
            manufacturer="Fabricante C",
            model="Batería inválida",
            capacity_kwh=8.0,
            max_charge_power_kw=5.0,
            max_discharge_power_kw=5.0,
            price_eur=2000.0,
            compatible_inverter_ids=(hybrid_inverter.id,),
            min_soc=0.9,
            max_soc=0.1,
        )


def test_battery_rejects_initial_soc_outside_limits(hybrid_inverter):
    with pytest.raises(ValueError, match="initial_soc"):
        BatteryProduct(
            id="battery-invalid",
            manufacturer="Fabricante C",
            model="Batería inválida",
            capacity_kwh=8.0,
            max_charge_power_kw=5.0,
            max_discharge_power_kw=5.0,
            price_eur=2000.0,
            compatible_inverter_ids=(hybrid_inverter.id,),
            min_soc=0.1,
            max_soc=0.9,
            initial_soc=0.95,
        )


def test_catalog_finds_components_by_identifier(
    panel,
    hybrid_inverter,
    battery,
):
    catalog = ComponentCatalog(
        panels=(panel,),
        inverters=(hybrid_inverter,),
        batteries=(battery,),
    )

    assert catalog.get_panel("panel-540") is panel
    assert catalog.get_inverter("inverter-hybrid-8") is hybrid_inverter
    assert catalog.get_battery("battery-8") is battery


def test_catalog_rejects_unknown_panel_identifier():
    catalog = ComponentCatalog()

    with pytest.raises(KeyError, match="Unknown panel identifier"):
        catalog.get_panel("does-not-exist")


def test_catalog_rejects_duplicate_identifiers(panel):
    duplicate_inverter = Inverter(
        id=panel.id,
        manufacturer="Fabricante B",
        model="Inversor",
        nominal_power_kw=5.0,
        max_pv_power_kwp=7.5,
        price_eur=900.0,
    )

    with pytest.raises(ValueError, match="Duplicate catalog identifier"):
        ComponentCatalog(
            panels=(panel,),
            inverters=(duplicate_inverter,),
        )


def test_catalog_rejects_battery_referencing_unknown_inverter():
    battery = BatteryProduct(
        id="battery-8",
        manufacturer="Fabricante C",
        model="Batería 8 kWh",
        capacity_kwh=8.0,
        max_charge_power_kw=5.0,
        max_discharge_power_kw=5.0,
        price_eur=2000.0,
        compatible_inverter_ids=("missing-inverter",),
    )

    with pytest.raises(ValueError, match="unknown inverters"):
        ComponentCatalog(batteries=(battery,))


def test_catalog_returns_compatible_batteries(
    hybrid_inverter,
    battery,
):
    incompatible_battery = BatteryProduct(
        id="battery-other",
        manufacturer="Fabricante E",
        model="Batería para otro equipo",
        capacity_kwh=5.0,
        max_charge_power_kw=3.0,
        max_discharge_power_kw=3.0,
        price_eur=1200.0,
        compatible_inverter_ids=("another-inverter",),
    )

    other_hybrid = Inverter(
        id="another-inverter",
        manufacturer="Fabricante F",
        model="Híbrido alternativo",
        nominal_power_kw=5.0,
        max_pv_power_kwp=7.5,
        price_eur=900.0,
        hybrid=True,
    )

    catalog = ComponentCatalog(
        inverters=(hybrid_inverter, other_hybrid),
        batteries=(battery, incompatible_battery),
    )

    assert catalog.compatible_batteries(
        hybrid_inverter.id
    ) == (battery,)



def test_catalog_returns_no_batteries_for_non_hybrid_inverter(battery):
    inverter = Inverter(
        id="inverter-standard",
        manufacturer="Fabricante G",
        model="Inversor estándar",
        nominal_power_kw=5.0,
        max_pv_power_kwp=7.5,
        price_eur=900.0,
        hybrid=False,
    )

    compatible_battery = replace(
        battery,
        compatible_inverter_ids=("inverter-standard",),
    )

    catalog = ComponentCatalog(
        inverters=(inverter,),
        batteries=(compatible_battery,),
    )

    assert catalog.compatible_batteries("inverter-standard") == ()

def test_mounting_system_requires_compatible_roof_types():
    with pytest.raises(ValueError, match="At least one"):
        MountingSystem(
            id="mounting-1",
            manufacturer="Fabricante H",
            model="Estructura",
            price_per_panel_eur=20.0,
            compatible_roof_types=(),
        )


def test_mounting_system_accepts_multiple_roof_types():
    mounting = MountingSystem(
        id="mounting-tile",
        manufacturer="Fabricante H",
        model="Estructura para teja",
        price_per_panel_eur=20.0,
        compatible_roof_types=("arabic_tile", "flat_tile"),
    )

    assert mounting.compatible_roof_types == (
        "arabic_tile",
        "flat_tile",
    )


@pytest.mark.parametrize(
    "basis",
    ["fixed", "per_panel", "per_kwp", "per_m2"],
)
def test_auxiliary_cost_accepts_supported_bases(basis):
    item = AuxiliaryCostItem(
        id=f"cost-{basis}",
        name="Coste auxiliar",
        unit_price_eur=100.0,
        basis=basis,
    )

    assert item.basis == basis


def test_auxiliary_cost_rejects_unknown_basis():
    with pytest.raises(ValueError, match="Unsupported cost basis"):
        AuxiliaryCostItem(
            id="cost-invalid",
            name="Coste auxiliar",
            unit_price_eur=100.0,
            basis="per_battery",
        )


def test_catalog_rejects_mutable_component_collections():
    with pytest.raises(TypeError, match="panels must be a tuple"):
        ComponentCatalog(panels=[])


def test_catalog_defaults_to_empty_collections():
    catalog = ComponentCatalog()

    assert catalog.panels == ()
    assert catalog.inverters == ()
    assert catalog.batteries == ()
    assert catalog.mounting_systems == ()
    assert catalog.auxiliary_costs == ()


def test_mounting_package_applies_successive_discounts():
    package_3 = MountingSystemPackage(
        id="mounting-package-3",
        mounting_system_id="mounting-arabic-tile",
        model="Soporte para 3 paneles",
        panel_capacity=3,
        quantity=4,
        unit_price_eur=125.00,
        discount_1_percent=40.0,
        discount_2_percent=3.0,
    )

    package_2 = MountingSystemPackage(
        id="mounting-package-2",
        mounting_system_id="mounting-arabic-tile",
        model="Soporte para 2 paneles",
        panel_capacity=2,
        quantity=2,
        unit_price_eur=87.00,
        discount_1_percent=40.0,
        discount_2_percent=3.0,
    )

    assert package_3.net_unit_price_eur == pytest.approx(72.75)
    assert package_3.total_price_eur == 291.00

    assert package_2.net_unit_price_eur == pytest.approx(50.634)
    assert package_2.total_price_eur == 101.27

    assert (
        package_3.total_price_eur + package_2.total_price_eur
    ) == 392.27

    assert (
        package_3.total_panel_capacity
        + package_2.total_panel_capacity
    ) == 16


@pytest.mark.parametrize(
    "field,value",
    [
        ("discount_1_percent", -1.0),
        ("discount_1_percent", 100.1),
        ("discount_2_percent", -1.0),
        ("discount_2_percent", 100.1),
    ],
)
def test_mounting_package_rejects_invalid_discounts(field, value):
    values = {
        "id": "mounting-package",
        "mounting_system_id": "mounting-arabic-tile",
        "model": "Soporte",
        "panel_capacity": 3,
        "quantity": 4,
        "unit_price_eur": 125.00,
        "discount_1_percent": 40.0,
        "discount_2_percent": 3.0,
    }
    values[field] = value

    with pytest.raises(ValueError):
        MountingSystemPackage(**values)
