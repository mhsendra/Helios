
"""Catálogo comercial inicial para la instalación fotovoltaica de Helios.

Los precios se expresan sin IVA.

Los precios netos identificados en el presupuesto se conservan tal como
fueron reconciliados. Los porcentajes de descuento documentan las
condiciones comerciales aplicables; no se recalculan los precios netos
a partir de tarifas reconstruidas que no se han confirmado documentalmente.

No se incluyen baterías ni sistemas de montaje mientras sus referencias
y precios comerciales no estén confirmados.
"""

from helios.solar.components_catalog import (
    AuxiliaryCostItem,
    ComponentCatalog,
    Inverter,
    PhotovoltaicPanel,
)


DISCOUNT_1_PERCENT = 40.0
DISCOUNT_2_PREMIUM_PERCENT = 1.5
DISCOUNT_2_STANDARD_PERCENT = 3.0


def build_default_component_catalog() -> ComponentCatalog:
    """Construye el catálogo con los precios netos comerciales identificados."""

    panel = PhotovoltaicPanel(
        id="longi lr7-60hvh-540m",
        manufacturer="Longi",
        model="LR7-60HVH-540M",
        power_wp=540.0,
        width_m=1.134,
        height_m=1.990,
        price_eur=92.196,
        technology="monocrystalline",
        discount_1_percent=DISCOUNT_1_PERCENT,
        discount_2_percent=DISCOUNT_2_PREMIUM_PERCENT,
    )

    inverter = Inverter(
        id="goodwe-gw8k-eha-g20",
        manufacturer="GoodWe",
        model="GW8K-EHA-G20",
        nominal_power_kw=8.0,
        max_pv_power_kwp=12.0,
        price_eur=960.38,
        hybrid=True,
        discount_1_percent=DISCOUNT_1_PERCENT,
        discount_2_percent=DISCOUNT_2_PREMIUM_PERCENT,
    )

    auxiliary_costs = (
        AuxiliaryCostItem(
            id="electrical_protection",
            name="Cajas de protección",
            unit_price_eur=343.96,
            basis="fixed",
            discount_1_percent=DISCOUNT_1_PERCENT,
            discount_2_percent=DISCOUNT_2_STANDARD_PERCENT,
        ),
        AuxiliaryCostItem(
            id="solar_cabling",
            name="Cable solar",
            unit_price_eur=110.58,
            basis="fixed",
            discount_1_percent=DISCOUNT_1_PERCENT,
            discount_2_percent=DISCOUNT_2_STANDARD_PERCENT,
        ),
        AuxiliaryCostItem(
            id="connector_female",
            name="Conector solar hembra",
            unit_price_eur=14.78,
            basis="fixed",
            discount_1_percent=DISCOUNT_1_PERCENT,
            discount_2_percent=DISCOUNT_2_PREMIUM_PERCENT,
        ),
        AuxiliaryCostItem(
            id="connector_male",
            name="Conector solar macho",
            unit_price_eur=14.18,
            basis="fixed",
            discount_1_percent=DISCOUNT_1_PERCENT,
            discount_2_percent=DISCOUNT_2_PREMIUM_PERCENT,
        ),
        AuxiliaryCostItem(
            id="joining_profiles",
            name="Perfiles de unión",
            unit_price_eur=8.27,
            basis="fixed",
            discount_1_percent=DISCOUNT_1_PERCENT,
            discount_2_percent=DISCOUNT_2_PREMIUM_PERCENT,
        ),
        AuxiliaryCostItem(
            id="installation",
            name="Mano de obra de instalación",
            unit_price_eur=2950.0,
            basis="fixed",
        ),
        AuxiliaryCostItem(
            id="legalization_estimate",
            name="Estimación de legalización",
            unit_price_eur=650.0,
            basis="fixed",
        ),
    )

    return ComponentCatalog(
        panels=(panel,),
        inverters=(inverter,),
        batteries=(),
        mounting_systems=(),
        auxiliary_costs=auxiliary_costs,
        mounting_packages=(),
    )
