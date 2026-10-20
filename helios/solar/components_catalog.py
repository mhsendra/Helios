
from __future__ import annotations

import math
from dataclasses import dataclass
from decimal import Decimal


DEFAULT_DISCOUNT_1_PERCENT = 40.0
DISCOUNT_2_PREMIUM_PERCENT = 1.5
DISCOUNT_2_STANDARD_PERCENT = 3.0


def _validate_text(name: str, value: str) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string.")
    if not value.strip():
        raise ValueError(f"{name} cannot be empty.")


def _validate_non_negative(name: str, value: float) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be numeric.")
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite.")
    if value < 0:
        raise ValueError(f"{name} cannot be negative.")


def _validate_positive(name: str, value: float) -> None:
    _validate_non_negative(name, value)
    if value <= 0:
        raise ValueError(f"{name} must be greater than zero.")


def _validate_discount(name: str, value: float) -> None:
    _validate_non_negative(name, value)
    if value > 100:
        raise ValueError(f"{name} cannot exceed 100%.")


def _net_price(
    list_price_eur: float,
    discount_1_percent: float,
    discount_2_percent: float,
) -> float:
    """Aplica los descuentos de forma sucesiva, sin sumarlos."""
    price = Decimal(str(list_price_eur))
    first = Decimal(str(discount_1_percent)) / Decimal("100")
    second = Decimal(str(discount_2_percent)) / Decimal("100")

    net = price * (Decimal("1") - first) * (Decimal("1") - second)
    return float(net)


def _validate_identifiers(name: str, values: tuple[str, ...]) -> None:
    if not isinstance(values, tuple):
        raise TypeError(f"{name} must be a tuple of identifiers.")
    for value in values:
        _validate_text(name, value)
    if len(values) != len(set(values)):
        raise ValueError(f"{name} cannot contain duplicate identifiers.")


@dataclass(frozen=True)
class PhotovoltaicPanel:
    """Referencia de catálogo de un panel fotovoltaico."""

    id: str
    manufacturer: str
    model: str
    power_wp: float
    width_m: float
    height_m: float
    price_eur: float
    technology: str = "monocrystalline"
    list_price_eur: float | None = None
    discount_1_percent: float = 0.0
    discount_2_percent: float = 0.0

    def __post_init__(self) -> None:
        for name in ("id", "manufacturer", "model", "technology"):
            _validate_text(name, getattr(self, name))

        for name in ("power_wp", "width_m", "height_m"):
            _validate_positive(name, getattr(self, name))

        _validate_non_negative("price_eur", self.price_eur)
        _validate_discount("discount_1_percent", self.discount_1_percent)
        _validate_discount("discount_2_percent", self.discount_2_percent)

        if self.list_price_eur is not None:
            _validate_non_negative("list_price_eur", self.list_price_eur)
            object.__setattr__(
                self,
                "price_eur",
                _net_price(
                    self.list_price_eur,
                    self.discount_1_percent,
                    self.discount_2_percent,
                ),
            )

    @property
    def area_m2(self) -> float:
        return self.width_m * self.height_m


@dataclass(frozen=True)
class Inverter:
    """Referencia de catálogo de un inversor."""

    id: str
    manufacturer: str
    model: str
    nominal_power_kw: float
    max_pv_power_kwp: float
    price_eur: float
    hybrid: bool = False
    list_price_eur: float | None = None
    discount_1_percent: float = 0.0
    discount_2_percent: float = 0.0

    def __post_init__(self) -> None:
        for name in ("id", "manufacturer", "model"):
            _validate_text(name, getattr(self, name))

        for name in ("nominal_power_kw", "max_pv_power_kwp"):
            _validate_positive(name, getattr(self, name))

        _validate_non_negative("price_eur", self.price_eur)
        _validate_discount("discount_1_percent", self.discount_1_percent)
        _validate_discount("discount_2_percent", self.discount_2_percent)

        if self.list_price_eur is not None:
            _validate_non_negative("list_price_eur", self.list_price_eur)
            object.__setattr__(
                self,
                "price_eur",
                _net_price(
                    self.list_price_eur,
                    self.discount_1_percent,
                    self.discount_2_percent,
                ),
            )

        if not isinstance(self.hybrid, bool):
            raise TypeError("hybrid must be a boolean.")


@dataclass(frozen=True)
class BatteryProduct:
    """Referencia de catálogo de una batería."""

    id: str
    manufacturer: str
    model: str
    capacity_kwh: float
    max_charge_power_kw: float
    max_discharge_power_kw: float
    price_eur: float
    compatible_inverter_ids: tuple[str, ...]
    charge_efficiency: float = 0.95
    discharge_efficiency: float = 0.95
    min_soc: float = 0.10
    max_soc: float = 0.90
    initial_soc: float = 0.50
    list_price_eur: float | None = None
    discount_1_percent: float = 0.0
    discount_2_percent: float = 0.0

    def __post_init__(self) -> None:
        for name in ("id", "manufacturer", "model"):
            _validate_text(name, getattr(self, name))

        for name in (
            "capacity_kwh",
            "max_charge_power_kw",
            "max_discharge_power_kw",
        ):
            _validate_positive(name, getattr(self, name))

        _validate_non_negative("price_eur", self.price_eur)
        _validate_discount("discount_1_percent", self.discount_1_percent)
        _validate_discount("discount_2_percent", self.discount_2_percent)

        if self.list_price_eur is not None:
            _validate_non_negative("list_price_eur", self.list_price_eur)
            object.__setattr__(
                self,
                "price_eur",
                _net_price(
                    self.list_price_eur,
                    self.discount_1_percent,
                    self.discount_2_percent,
                ),
            )

        _validate_identifiers(
            "compatible_inverter_ids",
            self.compatible_inverter_ids,
        )
        _validate_efficiency("charge_efficiency", self.charge_efficiency)
        _validate_efficiency("discharge_efficiency", self.discharge_efficiency)

        for name in ("min_soc", "max_soc", "initial_soc"):
            value = getattr(self, name)
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
            ):
                raise ValueError(f"{name} must be a finite number.")

        if not 0 <= self.min_soc < self.max_soc <= 1:
            raise ValueError(
                "SOC limits must satisfy 0 <= min_soc < max_soc <= 1."
            )
        if not self.min_soc <= self.initial_soc <= self.max_soc:
            raise ValueError(
                "initial_soc must be between min_soc and max_soc."
            )

    def is_compatible_with(self, inverter: Inverter) -> bool:
        if not isinstance(inverter, Inverter):
            raise TypeError("inverter must be an Inverter.")
        return inverter.id in self.compatible_inverter_ids


def _validate_efficiency(name: str, value: float) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be numeric.")
    if not math.isfinite(value) or not 0 < value <= 1:
        raise ValueError(f"{name} must be in the interval (0, 1].")


@dataclass(frozen=True)
class MountingSystem:
    """Sistema de montaje; admite el coste tradicional por panel."""

    id: str
    manufacturer: str
    model: str
    price_per_panel_eur: float
    compatible_roof_types: tuple[str, ...]

    def __post_init__(self) -> None:
        for name in ("id", "manufacturer", "model"):
            _validate_text(name, getattr(self, name))

        _validate_non_negative(
            "price_per_panel_eur",
            self.price_per_panel_eur,
        )

        if not self.compatible_roof_types:
            raise ValueError(
                "At least one compatible roof type is required."
            )

        _validate_identifiers(
            "compatible_roof_types",
            self.compatible_roof_types,
        )


@dataclass(frozen=True)
class MountingSystemPackage:
    """
    Conjunto comercial de montaje.

    unit_price_eur es el precio de tarifa por conjunto.
    Los descuentos se aplican sucesivamente.
    """

    id: str
    mounting_system_id: str
    model: str
    panel_capacity: int
    quantity: int
    unit_price_eur: float
    discount_1_percent: float = 0.0
    discount_2_percent: float = 0.0

    def __post_init__(self) -> None:
        for name in ("id", "mounting_system_id", "model"):
            _validate_text(name, getattr(self, name))

        for name in ("panel_capacity", "quantity"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{name} must be an integer.")
            if value <= 0:
                raise ValueError(f"{name} must be greater than zero.")

        _validate_non_negative("unit_price_eur", self.unit_price_eur)
        _validate_discount("discount_1_percent", self.discount_1_percent)
        _validate_discount("discount_2_percent", self.discount_2_percent)

    @property
    def net_unit_price_eur(self) -> float:
        return _net_price(
            self.unit_price_eur,
            self.discount_1_percent,
            self.discount_2_percent,
        )

    @property
    def total_panel_capacity(self) -> int:
        return self.panel_capacity * self.quantity

    @property
    def total_price_eur(self) -> float:
        total = (
            Decimal(str(self.unit_price_eur))
            * (
                Decimal("1")
                - Decimal(str(self.discount_1_percent)) / Decimal("100")
            )
            * (
                Decimal("1")
                - Decimal(str(self.discount_2_percent)) / Decimal("100")
            )
            * self.quantity
        )
        return float(total.quantize(Decimal("0.01")))


@dataclass(frozen=True)
class AuxiliaryCostItem:
    """
    Coste auxiliar configurable.

    basis admite fixed, per_panel, per_kwp o per_m2.

    Para los artículos comerciales, unit_price_eur se convierte
    en precio neto cuando se proporciona list_price_eur.
    Mano de obra y legalización deben usar descuentos del 0 %.
    """

    id: str
    name: str
    unit_price_eur: float
    basis: str
    list_price_eur: float | None = None
    discount_1_percent: float = 0.0
    discount_2_percent: float = 0.0

    VALID_BASES = frozenset({
        "fixed",
        "per_panel",
        "per_kwp",
        "per_m2",
    })

    def __post_init__(self) -> None:
        _validate_text("id", self.id)
        _validate_text("name", self.name)
        _validate_non_negative("unit_price_eur", self.unit_price_eur)
        _validate_discount("discount_1_percent", self.discount_1_percent)
        _validate_discount("discount_2_percent", self.discount_2_percent)

        if self.basis not in self.VALID_BASES:
            raise ValueError(f"Unsupported cost basis: {self.basis!r}.")

        if self.list_price_eur is not None:
            _validate_non_negative("list_price_eur", self.list_price_eur)
            object.__setattr__(
                self,
                "unit_price_eur",
                _net_price(
                    self.list_price_eur,
                    self.discount_1_percent,
                    self.discount_2_percent,
                ),
            )


@dataclass(frozen=True)
class ComponentCatalog:
    """Catálogo inmutable de equipos, estructuras y costes auxiliares."""

    panels: tuple[PhotovoltaicPanel, ...] = ()
    inverters: tuple[Inverter, ...] = ()
    batteries: tuple[BatteryProduct, ...] = ()
    mounting_systems: tuple[MountingSystem, ...] = ()
    auxiliary_costs: tuple[AuxiliaryCostItem, ...] = ()
    mounting_packages: tuple[MountingSystemPackage, ...] = ()

    def __post_init__(self) -> None:
        collections = (
            ("panels", self.panels, PhotovoltaicPanel),
            ("inverters", self.inverters, Inverter),
            ("batteries", self.batteries, BatteryProduct),
            ("mounting_systems", self.mounting_systems, MountingSystem),
            ("auxiliary_costs", self.auxiliary_costs, AuxiliaryCostItem),
            (
                "mounting_packages",
                self.mounting_packages,
                MountingSystemPackage,
            ),
        )

        all_ids: set[str] = set()
        for name, items, expected_type in collections:
            if not isinstance(items, tuple):
                raise TypeError(f"{name} must be a tuple.")

            for item in items:
                if not isinstance(item, expected_type):
                    raise TypeError(
                        f"Every item in {name} must be a "
                        f"{expected_type.__name__}."
                    )

                if item.id in all_ids:
                    raise ValueError(
                        f"Duplicate catalog identifier: {item.id!r}."
                    )
                all_ids.add(item.id)

        inverter_ids = {item.id for item in self.inverters}
        for battery in self.batteries:
            unknown_ids = set(battery.compatible_inverter_ids) - inverter_ids
            if unknown_ids:
                raise ValueError(
                    f"Battery {battery.id!r} references unknown "
                    f"inverters: {sorted(unknown_ids)!r}."
                )

        mounting_ids = {item.id for item in self.mounting_systems}
        for package in self.mounting_packages:
            if package.mounting_system_id not in mounting_ids:
                raise ValueError(
                    f"Mounting package {package.id!r} references unknown "
                    f"mounting system {package.mounting_system_id!r}."
                )

    def get_panel(self, component_id: str) -> PhotovoltaicPanel:
        return self._get_by_id(self.panels, component_id, "panel")

    def get_inverter(self, component_id: str) -> Inverter:
        return self._get_by_id(self.inverters, component_id, "inverter")

    def get_battery(self, component_id: str) -> BatteryProduct:
        return self._get_by_id(self.batteries, component_id, "battery")

    def get_mounting_system(self, component_id: str) -> MountingSystem:
        return self._get_by_id(
            self.mounting_systems,
            component_id,
            "mounting system",
        )

    def get_mounting_package(
        self,
        component_id: str,
    ) -> MountingSystemPackage:
        return self._get_by_id(
            self.mounting_packages,
            component_id,
            "mounting package",
        )

    def _get_by_id(self, items, component_id: str, category: str):
        _validate_text("component_id", component_id)
        for item in items:
            if item.id == component_id:
                return item

        raise KeyError(
            f"Unknown {category} identifier: {component_id!r}."
        )

    def compatible_batteries(
        self,
        inverter_id: str,
    ) -> tuple[BatteryProduct, ...]:
        inverter = self.get_inverter(inverter_id)
        if not inverter.hybrid:
            return ()

        return tuple(
            battery
            for battery in self.batteries
            if battery.is_compatible_with(inverter)
        )
