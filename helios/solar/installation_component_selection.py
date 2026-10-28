
"""Selection of commercial components for a PV installation."""

from dataclasses import dataclass, replace

from helios.solar.components_catalog import (
    AuxiliaryCostItem,
    BatteryProduct,
    ComponentCatalog,
    Inverter,
    MountingSystem,
    MountingSystemPackage,
    PhotovoltaicPanel,
)
from helios.solar.installation_configuration import (
    InstallationConfiguration,
)


@dataclass(frozen=True)
class InstallationComponentSelection:
    """Selected catalog products for a photovoltaic installation."""

    catalog: ComponentCatalog
    panel_id: str
    inverter_id: str
    mounting_system_id: str | None
    roof_type: str
    battery_id: str | None = None
    auxiliary_cost_ids: tuple[str, ...] = ()
    mounting_package_ids: tuple[str, ...] = ()
    mounting_package_panel_count: int | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.catalog, ComponentCatalog):
            raise TypeError("catalog must be a ComponentCatalog.")

        for name, value in (
            ("panel_id", self.panel_id),
            ("inverter_id", self.inverter_id),
            ("roof_type", self.roof_type),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string.")

        if self.mounting_system_id is not None and (
            not isinstance(self.mounting_system_id, str)
            or not self.mounting_system_id.strip()
        ):
            raise ValueError(
                "mounting_system_id must be None or a non-empty string."
            )

        if self.battery_id is not None and (
            not isinstance(self.battery_id, str)
            or not self.battery_id.strip()
        ):
            raise ValueError(
                "battery_id must be None or a non-empty string."
            )

        self._validate_id_tuple(
            "auxiliary_cost_ids",
            self.auxiliary_cost_ids,
        )
        self._validate_id_tuple(
            "mounting_package_ids",
            self.mounting_package_ids,
        )

        if self.mounting_package_panel_count is not None:
            value = self.mounting_package_panel_count
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(
                    "mounting_package_panel_count must be an integer or None."
                )
            if value <= 0:
                raise ValueError(
                    "mounting_package_panel_count must be greater than zero."
                )

        if self.mounting_package_ids and (
            self.mounting_package_panel_count is None
        ):
            raise ValueError(
                "mounting_package_panel_count is required when "
                "mounting packages are selected."
            )

        if not self.mounting_package_ids and (
            self.mounting_package_panel_count is not None
        ):
            raise ValueError(
                "mounting_package_panel_count requires selected "
                "mounting packages."
            )

        # Resolve selected references before accepting the selection.
        _ = self.panel
        inverter = self.inverter
        mounting = self.mounting_system

        if mounting is None and self.mounting_package_ids:
            raise ValueError(
                "Mounting packages cannot be selected without "
                "a mounting system."
            )

        if mounting is not None:
            if self.roof_type not in mounting.compatible_roof_types:
                raise ValueError(
                    f"Mounting system {mounting.id!r} is not compatible "
                    f"with roof type {self.roof_type!r}."
                )

        if self.battery_id is not None:
            if not inverter.hybrid:
                raise ValueError(
                    "A battery cannot be selected with a non-hybrid inverter."
                )
            if not self.battery.is_compatible_with(inverter):
                raise ValueError(
                    f"Battery {self.battery.id!r} is not compatible "
                    f"with inverter {inverter.id!r}."
                )

        auxiliary_ids = {
            item.id for item in self.catalog.auxiliary_costs
        }
        unknown_auxiliary_ids = (
            set(self.auxiliary_cost_ids) - auxiliary_ids
        )
        if unknown_auxiliary_ids:
            raise ValueError(
                "Unknown auxiliary cost identifiers: "
                f"{sorted(unknown_auxiliary_ids)!r}."
            )

        for package in self.mounting_packages:
            if mounting is None or package.mounting_system_id != mounting.id:
                raise ValueError(
                    f"Mounting package {package.id!r} does not belong "
                    "to the selected mounting system."
                )

        if self.mounting_packages:
            total_capacity = sum(
                package.total_panel_capacity
                for package in self.mounting_packages
            )
            if total_capacity < self.mounting_package_panel_count:
                raise ValueError(
                    "Selected mounting packages do not provide enough "
                    "positions for the quoted panel count."
                )

    @staticmethod
    def _validate_id_tuple(name: str, values: tuple[str, ...]) -> None:
        if not isinstance(values, tuple):
            raise TypeError(f"{name} must be a tuple.")
        if any(
            not isinstance(identifier, str) or not identifier.strip()
            for identifier in values
        ):
            raise ValueError(f"{name} must contain non-empty strings.")
        if len(set(values)) != len(values):
            raise ValueError(f"{name} cannot contain duplicates.")

    @property
    def panel(self) -> PhotovoltaicPanel:
        return self.catalog.get_panel(self.panel_id)

    @property
    def inverter(self) -> Inverter:
        return self.catalog.get_inverter(self.inverter_id)

    @property
    def battery(self) -> BatteryProduct:
        if self.battery_id is None:
            raise ValueError("No battery has been selected.")
        return self.catalog.get_battery(self.battery_id)

    @property
    def mounting_system(self) -> MountingSystem | None:
        if self.mounting_system_id is None:
            return None
        return self.catalog.get_mounting_system(self.mounting_system_id)

    @property
    def mounting_packages(self) -> tuple[MountingSystemPackage, ...]:
        return tuple(
            self.catalog.get_mounting_package(package_id)
            for package_id in self.mounting_package_ids
        )

    @property
    def mounting_package_total_cost_eur(self) -> float:
        return float(
            sum(
                package.total_price_eur
                for package in self.mounting_packages
            )
        )

    @property
    def auxiliary_costs(self) -> tuple[AuxiliaryCostItem, ...]:
        selected_ids = set(self.auxiliary_cost_ids)
        return tuple(
            item
            for item in self.catalog.auxiliary_costs
            if item.id in selected_ids
        )

    def apply_to(
        self,
        configuration: InstallationConfiguration,
    ) -> InstallationConfiguration:
        """Return a physical configuration using the selected panel."""

        if not isinstance(configuration, InstallationConfiguration):
            raise TypeError(
                "configuration must be an InstallationConfiguration."
            )

        panel = self.panel
        inverter = self.inverter

        maximum_by_inverter = int(
            inverter.max_pv_power_kwp * 1000 // panel.power_wp
        )

        if configuration.min_panels > maximum_by_inverter:
            raise ValueError(
                "Minimum number of panels exceeds the inverter's "
                "maximum PV power."
            )

        if configuration.max_panels is None:
            effective_maximum = maximum_by_inverter
        else:
            effective_maximum = min(
                configuration.max_panels,
                maximum_by_inverter,
            )

        return replace(
            configuration,
            panel_width_m=panel.width_m,
            panel_height_m=panel.height_m,
            panel_power_wp=panel.power_wp,
            max_panels=effective_maximum,
        )
