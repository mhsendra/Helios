"""Catálogo comercial inicial de componentes fotovoltaicos Helios.

Todos los importes están expresados sin IVA.

Los equipos comerciales utilizan precio de tarifa y descuentos
sucesivos. Los accesorios con precio neto reconciliado conservan
ese importe sin volver a aplicar descuentos.
"""

from helios.solar.components_catalog import (
    AuxiliaryCostItem,
    BatteryProduct,
    ComponentCatalog,
    Inverter,
    MountingSystem,
    MountingSystemPackage,
    PhotovoltaicPanel,
)


DISCOUNT_1_PERCENT = 40.0
DISCOUNT_2_PREMIUM_PERCENT = 1.5
DISCOUNT_2_STANDARD_PERCENT = 3.0

def build_default_component_catalog() -> ComponentCatalog:
    """Construye el catálogo comercial predeterminado de Helios."""

    inverter_id = "goodwe-gw8k-eha-g20"

    panel = PhotovoltaicPanel(
        id="longi lr7-60hvh-540m",
        manufacturer="Longi",
        model="LR7-60HVH-540M",
        power_wp=540.0,
        width_m=1.134,
        height_m=1.990,
        price_eur=0.0,
        technology="monocrystalline",
        list_price_eur=156.00,
        discount_1_percent=DISCOUNT_1_PERCENT,
        discount_2_percent=DISCOUNT_2_PREMIUM_PERCENT,
    )

    inverter = Inverter(
        id=inverter_id,
        manufacturer="GoodWe",
        model="GW8K-EHA-G20",
        nominal_power_kw=8.0,
        max_pv_power_kwp=12.0,
        price_eur=0.0,
        hybrid=True,
        list_price_eur=1625.00,
        discount_1_percent=DISCOUNT_1_PERCENT,
        discount_2_percent=DISCOUNT_2_PREMIUM_PERCENT,
    )

    # Only the 15-panel Arabic-tile roof package has a confirmed price.
    # Do not extrapolate this quote to other panel counts.
    mounting_system = MountingSystem(
        id="mounting-arabic-tile",
        manufacturer="Sistema de montaje",
        model="Teja árabe (tarifa por paquete)",
        price_per_panel_eur=None,
        compatible_roof_types=("teja_arabe",),
    )

    mounting_packages = (
        MountingSystemPackage(
            id="mounting-arabic-tile-3-panel",
            mounting_system_id=mounting_system.id,
            model="Soporte para 3 paneles",
            panel_capacity=3,
            quantity=4,
            unit_price_eur=125.00,
            discount_1_percent=40.0,
            discount_2_percent=3.0,
        ),
        MountingSystemPackage(
            id="mounting-arabic-tile-2-panel",
            mounting_system_id=mounting_system.id,
            model="Soporte para 2 paneles",
            panel_capacity=2,
            quantity=2,
            unit_price_eur=87.00,
            discount_1_percent=40.0,
            discount_2_percent=3.0,
        ),
    )

    auxiliary_costs = (
        AuxiliaryCostItem(
            id="electrical_protection_dc",
            name="Caja de protección DC",
            unit_price_eur=0.0,
            basis="fixed",
            list_price_eur=415.00,
            discount_1_percent=DISCOUNT_1_PERCENT,
            discount_2_percent=DISCOUNT_2_STANDARD_PERCENT,
        ),
        AuxiliaryCostItem(
            id="electrical_protection_ac",
            name="Caja de protección AC",
            unit_price_eur=0.0,
            basis="fixed",
            list_price_eur=176.00,
            discount_1_percent=DISCOUNT_1_PERCENT,
            discount_2_percent=DISCOUNT_2_STANDARD_PERCENT,
        ),
        AuxiliaryCostItem(
            id="solar_cabling_red",
            name="Cable solar rojo",
            unit_price_eur=0.0,
            basis="per_metre",
            list_price_eur=1.90,
            discount_1_percent=DISCOUNT_1_PERCENT,
            discount_2_percent=DISCOUNT_2_STANDARD_PERCENT,
            quantity=50.0,
        ),
        AuxiliaryCostItem(
            id="solar_cabling_black",
            name="Cable solar negro",
            unit_price_eur=0.0,
            basis="per_metre",
            list_price_eur=1.90,
            discount_1_percent=DISCOUNT_1_PERCENT,
            discount_2_percent=DISCOUNT_2_STANDARD_PERCENT,
            quantity=50.0,
        ),
        AuxiliaryCostItem(
            id="connector_female",
            name="Conector solar hembra",
            unit_price_eur=14.78,
            basis="fixed",
        ),
        AuxiliaryCostItem(
            id="connector_male",
            name="Conector solar macho",
            unit_price_eur=14.18,
            basis="fixed",
        ),
        AuxiliaryCostItem(
            id="joining_profiles",
            name="Perfiles de unión (2 unidades)",
            unit_price_eur=8.27,
            basis="fixed",
        ),
        AuxiliaryCostItem(
            id="installation",
            name="Mano de obra de instalación",
            unit_price_eur=2950.00,
            basis="fixed",
        ),
        AuxiliaryCostItem(
            id="legalization_estimate",
            name="Estimación de legalización",
            unit_price_eur=650.00,
            basis="fixed",
        ),
    )

    return ComponentCatalog(
        panels=(panel,),
        inverters=(inverter,),
        batteries=(),
        mounting_systems=(mounting_system,),
        auxiliary_costs=auxiliary_costs,
        mounting_packages=mounting_packages,
    )