"""Tests for commercial component selection for PV installations."""

from dataclasses import FrozenInstanceError

import pytest

from helios.solar.components_catalog import (
    AuxiliaryCostItem,
    BatteryProduct,
    ComponentCatalog,
    Inverter,
    MountingSystem,
    PhotovoltaicPanel,
)
from helios.solar.installation_component_selection import (
    InstallationComponentSelection,
)
from helios.solar.installation_configuration import InstallationConfiguration


@pytest.fixture
def panel() -> PhotovoltaicPanel:
    return PhotovoltaicPanel(
        id="panel-540",
        manufacturer="Longi",
        model="LR5-72HTH-540M",
        power_wp=540.0,
        width_m=2.256,
        height_m=1.133,
        price_eur=100.0,
        technology="monocrystalline",
    )


@pytest.fixture
def hybrid_inverter() -> Inverter:
    return Inverter(
        id="inverter-hybrid-8",
        manufacturer="GoodWe",
        model="GW8K-EHA",
        nominal_power_kw=8.0,
        max_pv_power_kwp=12.0,
        price_eur=1500.0,
        hybrid=True,
    )


@pytest.fixture
def string_inverter() -> Inverter:
    return Inverter(
        id="inverter-string-6",
        manufacturer="Example",
        model="String-6",
        nominal_power_kw=6.0,
        max_pv_power_kwp=8.0,
        price_eur=900.0,
        hybrid=False,
    )


@pytest.fixture
def battery(hybrid_inverter: Inverter) -> BatteryProduct:
    return BatteryProduct(
        id="battery-8",
        manufacturer="GoodWe",
        model="BAT-8",
        capacity_kwh=8.3,
        max_charge_power_kw=5.0,
        max_discharge_power_kw=5.0,
        price_eur=2000.0,
        compatible_inverter_ids=(hybrid_inverter.id,),
        charge_efficiency=0.95,
        discharge_efficiency=0.95,
        min_soc=0.10,
        max_soc=0.90,
        initial_soc=0.50,
    )


@pytest.fixture
def mounting_system() -> MountingSystem:
    return MountingSystem(
        id="mounting-tile",
        manufacturer="Example",
        model="Tile-Roof",
        price_per_panel_eur=20.0,
        compatible_roof_types=("arabic_tile", "concrete_tile"),
    )


@pytest.fixture
def auxiliary_cost() -> AuxiliaryCostItem:
    return AuxiliaryCostItem(
        id="legalization",
        name="Legalización",
        unit_price_eur=650.0,
        basis="fixed",
    )


@pytest.fixture
def catalog(
    panel: PhotovoltaicPanel,
    hybrid_inverter: Inverter,
    string_inverter: Inverter,
    battery: BatteryProduct,
    mounting_system: MountingSystem,
    auxiliary_cost: AuxiliaryCostItem,
) -> ComponentCatalog:
    return ComponentCatalog(
        panels=(panel,),
        inverters=(hybrid_inverter, string_inverter),
        batteries=(battery,),
        mounting_systems=(mounting_system,),
        auxiliary_costs=(auxiliary_cost,),
    )


@pytest.fixture
def configuration() -> InstallationConfiguration:
    return InstallationConfiguration(
        available_area_m2=40.0,
        panel_width_m=1.0,
        panel_height_m=1.0,
        panel_power_wp=400.0,
        min_panels=1,
        max_panels=30,
        panel_orientation="vertical",
        maintenance_passage_required=False,
    )


@pytest.fixture
def selection(catalog: ComponentCatalog) -> InstallationComponentSelection:
    return InstallationComponentSelection(
        catalog=catalog,
        panel_id="panel-540",
        inverter_id="inverter-hybrid-8",
        mounting_system_id="mounting-tile",
        roof_type="arabic_tile",
        battery_id="battery-8",
        auxiliary_cost_ids=("legalization",),
    )


class TestInstallationComponentSelection:
    def test_resolves_selected_components(
        self,
        selection: InstallationComponentSelection,
        panel: PhotovoltaicPanel,
        hybrid_inverter: Inverter,
        battery: BatteryProduct,
        mounting_system: MountingSystem,
        auxiliary_cost: AuxiliaryCostItem,
    ) -> None:
        assert selection.panel == panel
        assert selection.inverter == hybrid_inverter
        assert selection.battery == battery
        assert selection.mounting_system == mounting_system
        assert selection.auxiliary_costs == (auxiliary_cost,)

    def test_apply_to_uses_selected_panel_dimensions_and_power(
        self,
        selection: InstallationComponentSelection,
        configuration: InstallationConfiguration,
    ) -> None:
        result = selection.apply_to(configuration)

        assert result.panel_width_m == 2.256
        assert result.panel_height_m == 1.133
        assert result.panel_power_wp == 540.0

    def test_apply_to_preserves_physical_configuration(
        self,
        selection: InstallationComponentSelection,
        configuration: InstallationConfiguration,
    ) -> None:
        result = selection.apply_to(configuration)

        assert result.available_area_m2 == configuration.available_area_m2
        assert result.min_panels == configuration.min_panels
        assert result.panel_orientation == configuration.panel_orientation
        assert (
            result.maintenance_passage_required
            == configuration.maintenance_passage_required
        )
        assert (
            result.maintenance_passage_width_m
            == configuration.maintenance_passage_width_m
        )
        assert (
            result.maintenance_passage_orientation
            == configuration.maintenance_passage_orientation
        )
        assert result.roof_width_m == configuration.roof_width_m
        assert result.roof_height_m == configuration.roof_height_m

    def test_apply_to_caps_panel_count_to_inverter_pv_limit(
        self,
        selection: InstallationComponentSelection,
        configuration: InstallationConfiguration,
    ) -> None:
        result = selection.apply_to(configuration)

        # 12 kWp / 540 Wp = 22 complete panels.
        assert result.max_panels == 22

    def test_apply_to_preserves_lower_existing_panel_limit(
        self,
        selection: InstallationComponentSelection,
        configuration: InstallationConfiguration,
    ) -> None:
        limited_configuration = InstallationConfiguration(
            available_area_m2=configuration.available_area_m2,
            panel_width_m=configuration.panel_width_m,
            panel_height_m=configuration.panel_height_m,
            panel_power_wp=configuration.panel_power_wp,
            min_panels=configuration.min_panels,
            max_panels=10,
        )

        result = selection.apply_to(limited_configuration)

        assert result.max_panels == 10

    def test_apply_to_rejects_minimum_above_inverter_limit(
        self,
        selection: InstallationComponentSelection,
        configuration: InstallationConfiguration,
    ) -> None:
        impossible_configuration = InstallationConfiguration(
            available_area_m2=configuration.available_area_m2,
            panel_width_m=configuration.panel_width_m,
            panel_height_m=configuration.panel_height_m,
            panel_power_wp=configuration.panel_power_wp,
            min_panels=23,
            max_panels=30,
        )

        with pytest.raises(ValueError):
            selection.apply_to(impossible_configuration)

    def test_rejects_mounting_system_incompatible_with_roof(
        self,
        catalog: ComponentCatalog,
    ) -> None:
        with pytest.raises(ValueError):
            InstallationComponentSelection(
                catalog=catalog,
                panel_id="panel-540",
                inverter_id="inverter-hybrid-8",
                mounting_system_id="mounting-tile",
                roof_type="flat_roof",
            )

    def test_rejects_battery_with_non_hybrid_inverter(
        self,
        catalog: ComponentCatalog,
    ) -> None:
        with pytest.raises(ValueError):
            InstallationComponentSelection(
                catalog=catalog,
                panel_id="panel-540",
                inverter_id="inverter-string-6",
                mounting_system_id="mounting-tile",
                roof_type="arabic_tile",
                battery_id="battery-8",
            )

    def test_rejects_unknown_panel(self, catalog: ComponentCatalog) -> None:
        with pytest.raises(KeyError, match="Unknown panel identifier"):
            InstallationComponentSelection(
                catalog=catalog,
                panel_id="unknown-panel",
                inverter_id="inverter-hybrid-8",
                mounting_system_id="mounting-tile",
                roof_type="arabic_tile",
            )

    def test_rejects_unknown_inverter(self, catalog: ComponentCatalog) -> None:
        with pytest.raises(KeyError, match="Unknown inverter identifier"):
            InstallationComponentSelection(
                catalog=catalog,
                panel_id="panel-540",
                inverter_id="unknown-inverter",
                mounting_system_id="mounting-tile",
                roof_type="arabic_tile",
            )

    def test_rejects_unknown_battery(self, catalog: ComponentCatalog) -> None:
        with pytest.raises(KeyError, match="Unknown battery identifier"):
            InstallationComponentSelection(
                catalog=catalog,
                panel_id="panel-540",
                inverter_id="inverter-hybrid-8",
                mounting_system_id="mounting-tile",
                roof_type="arabic_tile",
                battery_id="unknown-battery",
            )

    def test_rejects_unknown_auxiliary_cost(
        self,
        catalog: ComponentCatalog,
    ) -> None:
        with pytest.raises(ValueError):
            InstallationComponentSelection(
                catalog=catalog,
                panel_id="panel-540",
                inverter_id="inverter-hybrid-8",
                mounting_system_id="mounting-tile",
                roof_type="arabic_tile",
                auxiliary_cost_ids=("unknown-cost",),
            )

    def test_rejects_duplicate_auxiliary_cost_ids(
        self,
        catalog: ComponentCatalog,
    ) -> None:
        with pytest.raises(ValueError):
            InstallationComponentSelection(
                catalog=catalog,
                panel_id="panel-540",
                inverter_id="inverter-hybrid-8",
                mounting_system_id="mounting-tile",
                roof_type="arabic_tile",
                auxiliary_cost_ids=("legalization", "legalization"),
            )

    def test_rejects_empty_component_identifiers(
        self,
        catalog: ComponentCatalog,
    ) -> None:
        with pytest.raises(ValueError):
            InstallationComponentSelection(
                catalog=catalog,
                panel_id=" ",
                inverter_id="inverter-hybrid-8",
                mounting_system_id="mounting-tile",
                roof_type="arabic_tile",
            )

    def test_selection_is_immutable(
        self,
        selection: InstallationComponentSelection,
    ) -> None:
        with pytest.raises(FrozenInstanceError):
            selection.panel_id = "another-panel"  # type: ignore[misc]

    def test_apply_to_does_not_mutate_original_configuration(
        self,
        selection: InstallationComponentSelection,
        configuration: InstallationConfiguration,
    ) -> None:
        original_values = (
            configuration.panel_width_m,
            configuration.panel_height_m,
            configuration.panel_power_wp,
            configuration.max_panels,
        )

        selection.apply_to(configuration)

        assert (
            configuration.panel_width_m,
            configuration.panel_height_m,
            configuration.panel_power_wp,
            configuration.max_panels,
        ) == original_values

    def test_rejects_invalid_configuration_type(
        self,
        selection: InstallationComponentSelection,
    ) -> None:
        with pytest.raises(TypeError):
            selection.apply_to(object())  # type: ignore[arg-type]
