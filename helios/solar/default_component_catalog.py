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

    # Sistema predeterminado: SUNFER 01V-CL con clip.
    # Los precios publicados incluyen IVA. Se convierten a netos
    # y no se aplican descuentos comerciales adicionales.
    mounting_system = MountingSystem(
        id="mounting-arabic-tile",
        manufacturer="SUNFER",
        model="01V-CL (clip), cubierta de teja",
        price_per_panel_eur=None,
        compatible_roof_types=("teja_arabe",),
    )

    mounting_system_l = MountingSystem(
        id="mounting-arabic-tile-l",
        manufacturer="SUNFER",
        model="01V-L (conexión L), cubierta de teja",
        price_per_panel_eur=None,
        compatible_roof_types=("teja_arabe",),
    )

    # Precios brutos publicados por capacidad de kit.
    # El catálogo de Helios almacena los precios sin IVA.
    clip_prices_gross = {
        1: 56.97,
        2: 90.83,
        3: 121.25,
        4: 150.78,
        5: 184.44,
        6: 217.95,
    }

    l_prices_gross = {
        1: 61.65,
        3: 125.20,
        4: 155.64,
        5: 191.53,
        6: 223.63,
    }

    mounting_packages = tuple(
        [
            MountingSystemPackage(
                id=f"sunfer-01v-cl-{capacity}-panel",
                mounting_system_id=mounting_system.id,
                model=f"SUNFER 01V-CL, {capacity} módulo(s)",
                panel_capacity=capacity,
                quantity=1,
                unit_price_eur=price_gross / 1.21,
            )
            for capacity, price_gross in clip_prices_gross.items()
        ]
        + [
            MountingSystemPackage(
                id=f"sunfer-01v-l-{capacity}-panel",
                mounting_system_id=mounting_system_l.id,
                model=f"SUNFER 01V-L, {capacity} módulo(s)",
                panel_capacity=capacity,
                quantity=1,
                unit_price_eur=price_gross / 1.21,
            )
            for capacity, price_gross in l_prices_gross.items()
        ]
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
        mounting_systems=(
            mounting_system,
            mounting_system_l,
        ),
        auxiliary_costs=auxiliary_costs,
        mounting_packages=mounting_packages,
    )
