
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING, Mapping

from helios.solar.battery_economic_model import (
    CombinedEconomicConfiguration,
)
from helios.solar.installation_evaluation import (
    InstallationEvaluation,
)

if TYPE_CHECKING:
    from helios.solar.components_catalog import AuxiliaryCostItem
    from helios.solar.installation_component_selection import (
        InstallationComponentSelection,
    )


@dataclass(frozen=True)
class InstallationCostConfiguration:
    """
    Configuración de costes de una instalación fotovoltaica.

    Los paneles y la estructura tradicional se calculan por unidad.
    También puede configurarse una oferta comercial de estructuras
    para un número concreto de paneles.

    La batería queda fuera del coste base y se gestiona por separado.
    Los precios deben expresarse todos en la misma base fiscal.
    """

    panel_unit_cost_eur: float
    structure_unit_cost_eur: float | None = 0.0
    installation_cost_eur: float = 0.0
    inverter_unit_cost_eur: float = 0.0
    electrical_protection_cost_eur: float = 0.0
    cabling_cost_eur: float = 0.0
    legalization_cost_eur: float = 0.0
    auxiliary_panel_area_m2: float | None = None
    auxiliary_cost_items: tuple["AuxiliaryCostItem", ...] = ()
    auxiliary_cost_categories: tuple[tuple[str, str], ...] = ()
    structure_package_cost_eur: float | None = None
    structure_package_panel_count: int | None = None

    _VALID_AUXILIARY_CATEGORIES = frozenset({
        "installation",
        "electrical_protection",
        "cabling",
        "legalization",
    })

    def __post_init__(self) -> None:
        fields = (
            ("panel_unit_cost_eur", self.panel_unit_cost_eur),
            ("installation_cost_eur", self.installation_cost_eur),
            ("inverter_unit_cost_eur", self.inverter_unit_cost_eur),
            (
                "electrical_protection_cost_eur",
                self.electrical_protection_cost_eur,
            ),
            ("cabling_cost_eur", self.cabling_cost_eur),
            ("legalization_cost_eur", self.legalization_cost_eur),
        )

        for name, value in fields:
            self._validate_non_negative_number(name, value)

        if self.structure_unit_cost_eur is not None:
            self._validate_non_negative_number(
                "structure_unit_cost_eur",
                self.structure_unit_cost_eur,
            )

        if self.structure_package_cost_eur is not None:
            self._validate_non_negative_number(
                "structure_package_cost_eur",
                self.structure_package_cost_eur,
            )

        if self.structure_package_panel_count is not None:
            value = self.structure_package_panel_count
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(
                    "structure_package_panel_count must be an integer or None."
                )
            if value <= 0:
                raise ValueError(
                    "structure_package_panel_count must be greater than zero."
                )

        if (
            (self.structure_package_cost_eur is None)
            != (self.structure_package_panel_count is None)
        ):
            raise ValueError(
                "structure_package_cost_eur and "
                "structure_package_panel_count must be set together."
            )

        if not isinstance(self.auxiliary_cost_items, tuple):
            raise TypeError("auxiliary_cost_items must be a tuple.")
        if not isinstance(self.auxiliary_cost_categories, tuple):
            raise TypeError("auxiliary_cost_categories must be a tuple.")

        item_ids: set[str] = set()
        for item in self.auxiliary_cost_items:
            if not hasattr(item, "id") or not hasattr(item, "basis"):
                raise TypeError(
                    "Every auxiliary cost must be an AuxiliaryCostItem."
                )
            if item.id in item_ids:
                raise ValueError(
                    f"Duplicate auxiliary cost identifier: {item.id}"
                )
            item_ids.add(item.id)

        mapped_ids: set[str] = set()
        for mapping in self.auxiliary_cost_categories:
            if not isinstance(mapping, tuple) or len(mapping) != 2:
                raise TypeError(
                    "Each auxiliary category mapping must be a "
                    "(cost_id, category) tuple."
                )

            cost_id, category = mapping

            if cost_id not in item_ids:
                raise ValueError(
                    f"Unknown auxiliary cost identifier: {cost_id}"
                )
            if category not in self._VALID_AUXILIARY_CATEGORIES:
                raise ValueError(
                    f"Unsupported auxiliary cost category: {category}"
                )
            if cost_id in mapped_ids:
                raise ValueError(
                    f"Auxiliary cost already mapped: {cost_id}"
                )
            mapped_ids.add(cost_id)

        if self.auxiliary_panel_area_m2 is not None:
            value = self.auxiliary_panel_area_m2
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError(
                    "auxiliary_panel_area_m2 must be numeric or None."
                )
            if not math.isfinite(value):
                raise ValueError("auxiliary_panel_area_m2 must be finite.")
            if value <= 0:
                raise ValueError(
                    "auxiliary_panel_area_m2 must be greater than zero."
                )

    @staticmethod
    def _validate_non_negative_number(name: str, value: float) -> None:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"{name} must be numeric.")
        if not math.isfinite(value):
            raise ValueError(f"{name} must be finite.")
        if value < 0:
            raise ValueError(f"{name} cannot be negative.")

    @classmethod
    def from_selection(
        cls,
        selection: "InstallationComponentSelection",
        *,
        auxiliary_cost_categories: Mapping[str, str] | None = None,
    ) -> "InstallationCostConfiguration":
        """Construye los costes desde la selección de catálogo."""

        from helios.solar.installation_component_selection import (
            InstallationComponentSelection,
        )

        if not isinstance(selection, InstallationComponentSelection):
            raise TypeError(
                "selection must be an InstallationComponentSelection."
            )

        if auxiliary_cost_categories is None:
            auxiliary_cost_categories = {}
        if not isinstance(auxiliary_cost_categories, Mapping):
            raise TypeError(
                "auxiliary_cost_categories must be a mapping."
            )

        selected_auxiliary_costs = selection.auxiliary_costs
        selected_ids = {item.id for item in selected_auxiliary_costs}

        for cost_id, category in auxiliary_cost_categories.items():
            if cost_id not in selected_ids:
                raise ValueError(f"Auxiliary cost is not selected: {cost_id}")
            if category not in cls._VALID_AUXILIARY_CATEGORIES:
                raise ValueError(
                    f"Unsupported auxiliary cost category: {category}"
                )

        category_totals = {
            category: 0.0
            for category in cls._VALID_AUXILIARY_CATEGORIES
        }
        category_mappings: list[tuple[str, str]] = []

        for item in selected_auxiliary_costs:
            category = auxiliary_cost_categories.get(item.id)
            if category is None:
                continue

            if item.basis == "fixed":
                amount = float(item.unit_price_eur)
            elif item.basis == "per_metre" and category == "cabling":
                amount = (
                    float(item.unit_price_eur)
                    * float(item.quantity)
                )
            else:
                raise ValueError(
                    f"Auxiliary cost {item.id!r} uses basis "
                    f"{item.basis!r}; this basis cannot be "
                    f"converted to a fixed amount for category "
                    f"{category!r}."
                )

            category_totals[category] += amount
            category_mappings.append((item.id, category))

        has_packages = bool(selection.mounting_packages)

        return cls(
            panel_unit_cost_eur=float(selection.panel.price_eur),
            structure_unit_cost_eur=(
                float(selection.mounting_system.price_per_panel_eur)
                if selection.mounting_system is not None
                else None
            ),
            installation_cost_eur=category_totals["installation"],
            inverter_unit_cost_eur=float(selection.inverter.price_eur),
            electrical_protection_cost_eur=category_totals[
                "electrical_protection"
            ],
            cabling_cost_eur=category_totals["cabling"],
            legalization_cost_eur=category_totals["legalization"],
            auxiliary_cost_items=tuple(selected_auxiliary_costs),
            auxiliary_cost_categories=tuple(category_mappings),
            auxiliary_panel_area_m2=float(selection.panel.area_m2),
            structure_package_cost_eur=(
                selection.mounting_package_total_cost_eur
                if has_packages
                else None
            ),
            structure_package_panel_count=(
                selection.mounting_package_panel_count
                if has_packages
                else None
            ),
        )

    def calculate_panel_cost(self, panel_count: int) -> float:
        """Calcula el coste de los paneles según su número."""
        if isinstance(panel_count, bool) or not isinstance(panel_count, int):
            raise TypeError("panel_count must be an integer.")
        if panel_count <= 0:
            raise ValueError("panel_count must be greater than zero.")
        return float(panel_count * self.panel_unit_cost_eur)

    def calculate_structure_cost(
        self,
        evaluation: InstallationEvaluation,
    ) -> float:
        """Calcula el coste de estructura si existe un precio confirmado."""

        self._validate_evaluation(evaluation)

        if (
            self.structure_package_cost_eur is not None
            and evaluation.panel_count == self.structure_package_panel_count
        ):
            return float(self.structure_package_cost_eur)

        if self.structure_unit_cost_eur is None:
            raise ValueError(
                "El coste de la estructura no está confirmado. "
                "No se puede calcular la inversión económica "
                "hasta disponer de un precio de montaje."
            )

        return float(
            evaluation.panel_count * self.structure_unit_cost_eur
        )

    def calculate_installation_service_cost(
        self,
        evaluation: InstallationEvaluation,
    ) -> float:
        self._validate_evaluation(evaluation)
        return float(self.installation_cost_eur)

    def calculate_inverter_cost(
        self,
        evaluation: InstallationEvaluation,
    ) -> float:
        self._validate_evaluation(evaluation)
        return float(self.inverter_unit_cost_eur)

    def calculate_electrical_protection_cost(
        self,
        evaluation: InstallationEvaluation,
    ) -> float:
        self._validate_evaluation(evaluation)
        return float(self.electrical_protection_cost_eur)

    def calculate_cabling_cost(
        self,
        evaluation: InstallationEvaluation,
    ) -> float:
        self._validate_evaluation(evaluation)
        return float(self.cabling_cost_eur)

    def calculate_legalization_cost(
        self,
        evaluation: InstallationEvaluation,
    ) -> float:
        self._validate_evaluation(evaluation)
        return float(self.legalization_cost_eur)

    def calculate_auxiliary_cost(
        self,
        cost_id: str,
        evaluation: InstallationEvaluation,
        selection: "InstallationComponentSelection",
    ) -> float:
        """Calcula un coste auxiliar según su base de cálculo."""
        self._validate_evaluation(evaluation)

        from helios.solar.installation_component_selection import (
            InstallationComponentSelection,
        )

        if not isinstance(selection, InstallationComponentSelection):
            raise TypeError(
                "selection must be an InstallationComponentSelection."
            )
        if not isinstance(cost_id, str):
            raise TypeError("cost_id must be a string.")

        item = next(
            (
                auxiliary
                for auxiliary in self.auxiliary_cost_items
                if auxiliary.id == cost_id
            ),
            None,
        )
        if item is None:
            raise KeyError(
                f"Unknown selected auxiliary cost identifier: {cost_id}"
            )

        unit_price = float(item.unit_price_eur)

        if item.basis == "fixed":
            return unit_price
        if item.basis == "per_panel":
            return unit_price * evaluation.panel_count
        if item.basis == "per_kwp":
            return unit_price * evaluation.installed_power_kwp
        if item.basis == "per_m2":
            return (
                unit_price
                * evaluation.panel_count
                * selection.panel.area_m2
            )
        if item.basis == "per_metre":
            return unit_price * float(item.quantity)
        raise ValueError(
            f"Unsupported auxiliary cost basis: {item.basis!r}"
        )

    def calculate_installation_cost(
        self,
        evaluation: InstallationEvaluation,
    ) -> float:
        """
        Incluye paneles, estructura, mano de obra, inversor,
        protecciones, cableado y costes auxiliares no asignados.

        Excluye legalización y batería.
        """
        self._validate_evaluation(evaluation)

        base_cost = (
            self.calculate_panel_cost(evaluation.panel_count)
            + self.calculate_structure_cost(evaluation)
            + self.calculate_installation_service_cost(evaluation)
            + self.calculate_inverter_cost(evaluation)
            + self.calculate_electrical_protection_cost(evaluation)
            + self.calculate_cabling_cost(evaluation)
        )
        return base_cost + self.calculate_unmapped_auxiliary_cost(evaluation)

    def build_economic_configuration(
        self,
        evaluation: InstallationEvaluation,
    ) -> CombinedEconomicConfiguration:
        """Añade legalización; la batería se contabiliza por separado."""
        self._validate_evaluation(evaluation)

        return CombinedEconomicConfiguration(
            installation_cost_eur=(
                self.calculate_installation_cost(evaluation)
                + self.calculate_legalization_cost(evaluation)
            ),
            battery_cost_eur=0.0,
            annual_pv_savings_eur=0.0,
            annual_battery_additional_savings_eur=0.0,
        )

    @staticmethod
    def _validate_evaluation(
        evaluation: InstallationEvaluation,
    ) -> None:
        if not isinstance(evaluation, InstallationEvaluation):
            raise TypeError(
                "evaluation must be an InstallationEvaluation."
            )

    def calculate_unmapped_auxiliary_cost(
        self,
        evaluation: InstallationEvaluation,
    ) -> float:
        """Calcula los costes auxiliares que aún no están contabilizados."""
        self._validate_evaluation(evaluation)

        mapped_ids = {
            cost_id for cost_id, _ in self.auxiliary_cost_categories
        }
        total = 0.0

        for item in self.auxiliary_cost_items:
            if item.id in mapped_ids:
                continue

            unit_price = float(item.unit_price_eur)
            if item.basis == "fixed":
                total += unit_price
            elif item.basis == "per_panel":
                total += unit_price * evaluation.panel_count
            elif item.basis == "per_kwp":
                total += unit_price * evaluation.installed_power_kwp
            elif item.basis == "per_m2":
                if self.auxiliary_panel_area_m2 is None:
                    raise ValueError(
                        "auxiliary_panel_area_m2 is required for "
                        "per_m2 auxiliary costs."
                    )
                total += (
                    unit_price
                    * evaluation.panel_count
                    * self.auxiliary_panel_area_m2
                )
            elif item.basis == "per_metre":
                total += unit_price * float(item.quantity)
            else:
                raise ValueError(
                    f"Unsupported auxiliary cost basis: {item.basis!r}"
                )

        return float(total)
