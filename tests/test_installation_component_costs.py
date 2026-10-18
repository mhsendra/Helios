"""Integration tests for component selection and installation costs."""

import pytest

import pandas as pd

from helios.core.consumption_scenario import ConsumptionScenario
from helios.core.energy_recommender import EnergyRecommender
from helios.solar.installation_configuration import InstallationConfiguration
from helios.solar.installation_coordinator import InstallationCoordinator
from helios.solar.installation_evaluation import InstallationEvaluator
from helios.solar.installation_optimizer import InstallationOptimizer
from helios.solar.installation_recommendation import InstallationRecommender
from helios.solar.production_profile import SolarProductionProfile


from helios.solar.components_catalog import (
    AuxiliaryCostItem,
    BatteryProduct,
    ComponentCatalog,
    Inverter,
    MountingSystem,
    PhotovoltaicPanel,
)
from helios.solar.installation_candidate import InstallationCandidate
from helios.solar.installation_component_selection import (
    InstallationComponentSelection,
)
from helios.solar.installation_costs import InstallationCostConfiguration
from helios.solar.installation_evaluation import InstallationEvaluation


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
def inverter() -> Inverter:
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
def battery(inverter: Inverter) -> BatteryProduct:
    return BatteryProduct(
        id="battery-8",
        manufacturer="GoodWe",
        model="BAT-8",
        capacity_kwh=8.3,
        max_charge_power_kw=5.0,
        max_discharge_power_kw=5.0,
        price_eur=2000.0,
        compatible_inverter_ids=(inverter.id,),
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
        compatible_roof_types=("arabic_tile",),
    )


@pytest.fixture
def auxiliary_costs() -> tuple[AuxiliaryCostItem, ...]:
    return (
        AuxiliaryCostItem(
            id="installation",
            name="Mano de obra",
            unit_price_eur=800.0,
            basis="fixed",
        ),
        AuxiliaryCostItem(
            id="protections",
            name="Protecciones eléctricas",
            unit_price_eur=180.0,
            basis="fixed",
        ),
        AuxiliaryCostItem(
            id="cabling",
            name="Cableado",
            unit_price_eur=120.0,
            basis="fixed",
        ),
        AuxiliaryCostItem(
            id="legalization",
            name="Legalización",
            unit_price_eur=650.0,
            basis="fixed",
        ),
        AuxiliaryCostItem(
            id="roof-work",
            name="Coste por superficie ocupada",
            unit_price_eur=10.0,
            basis="per_m2",
        ),
        AuxiliaryCostItem(
            id="power-work",
            name="Coste por potencia",
            unit_price_eur=50.0,
            basis="per_kwp",
        ),
        AuxiliaryCostItem(
            id="panel-work",
            name="Coste por panel",
            unit_price_eur=5.0,
            basis="per_panel",
        ),
    )


@pytest.fixture
def catalog(
    panel: PhotovoltaicPanel,
    inverter: Inverter,
    battery: BatteryProduct,
    mounting_system: MountingSystem,
    auxiliary_costs: tuple[AuxiliaryCostItem, ...],
) -> ComponentCatalog:
    return ComponentCatalog(
        panels=(panel,),
        inverters=(inverter,),
        batteries=(battery,),
        mounting_systems=(mounting_system,),
        auxiliary_costs=auxiliary_costs,
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
        auxiliary_cost_ids=(
            "installation",
            "protections",
            "cabling",
            "legalization",
            "roof-work",
            "power-work",
            "panel-work",
        ),
    )


@pytest.fixture
def evaluation() -> InstallationEvaluation:
    candidate = InstallationCandidate(
        panel_count=10,
        panel_power_wp=540.0,
        panel_area_m2=2.256 * 1.133,
    )
    return InstallationEvaluation(
        candidate=candidate,
        available_area_m2=40.0,
    )


class TestInstallationComponentCosts:

    @staticmethod
    def _build_costs(
        selection: InstallationComponentSelection,
    ) -> InstallationCostConfiguration:
        return InstallationCostConfiguration.from_selection(
            selection,
            auxiliary_cost_categories={
                "installation": "installation",
                "protections": "electrical_protection",
                "cabling": "cabling",
                "legalization": "legalization",
            },
        )

    def test_from_selection_uses_selected_panel_price(
        self,
        selection: InstallationComponentSelection,
    ) -> None:
        costs = InstallationCostConfiguration.from_selection(selection)

        assert costs.panel_unit_cost_eur == 100.0

    def test_from_selection_uses_selected_mounting_price(
        self,
        selection: InstallationComponentSelection,
    ) -> None:
        costs = InstallationCostConfiguration.from_selection(selection)

        assert costs.structure_unit_cost_eur == 20.0

    def test_from_selection_uses_selected_inverter_price(
        self,
        selection: InstallationComponentSelection,
    ) -> None:
        costs = InstallationCostConfiguration.from_selection(selection)

        assert costs.inverter_unit_cost_eur == 1500.0

    def test_from_selection_maps_fixed_auxiliary_costs(
        self,
        selection: InstallationComponentSelection,
    ) -> None:
        costs = self._build_costs(selection)

        assert costs.installation_cost_eur == 800.0
        assert costs.electrical_protection_cost_eur == 180.0
        assert costs.cabling_cost_eur == 120.0
        assert costs.legalization_cost_eur == 650.0

    def test_auxiliary_cost_per_panel_uses_panel_count(
        self,
        selection: InstallationComponentSelection,
        evaluation: InstallationEvaluation,
    ) -> None:
        costs = InstallationCostConfiguration.from_selection(selection)

        # 5 € × 10 panels.
        assert costs.calculate_auxiliary_cost(
            "panel-work",
            evaluation,
            selection,
        ) == 50.0

    def test_auxiliary_cost_per_kwp_uses_installed_power(
        self,
        selection: InstallationComponentSelection,
        evaluation: InstallationEvaluation,
    ) -> None:
        costs = InstallationCostConfiguration.from_selection(selection)

        # 50 € × 5.4 kWp.
        assert costs.calculate_auxiliary_cost(
            "power-work",
            evaluation,
            selection,
        ) == pytest.approx(270.0)

    def test_auxiliary_cost_per_m2_uses_occupied_panel_area(
        self,
        selection: InstallationComponentSelection,
        evaluation: InstallationEvaluation,
    ) -> None:
        costs = InstallationCostConfiguration.from_selection(selection)

        expected_area = 10 * 2.256 * 1.133

        assert costs.calculate_auxiliary_cost(
            "roof-work",
            evaluation,
            selection,
        ) == pytest.approx(expected_area * 10.0)

    def test_auxiliary_fixed_cost_is_not_scaled(
        self,
        selection: InstallationComponentSelection,
        evaluation: InstallationEvaluation,
    ) -> None:
        costs = InstallationCostConfiguration.from_selection(selection)

        assert costs.calculate_auxiliary_cost(
            "installation",
            evaluation,
            selection,
        ) == 800.0

    def test_battery_is_not_included_in_base_installation_cost(
        self,
        selection: InstallationComponentSelection,
    ) -> None:
        costs = InstallationCostConfiguration.from_selection(selection)

        assert costs.inverter_unit_cost_eur == 1500.0
        assert costs.panel_unit_cost_eur == 100.0

        # The battery price is handled by the battery optimizer,
        # not by the base installation cost configuration.
        assert selection.battery.price_eur == 2000.0

    
    def test_legalization_is_excluded_from_installation_cost(
        self,
        selection: InstallationComponentSelection,
        evaluation: InstallationEvaluation,
    ) -> None:
        costs = self._build_costs(selection)

        expected_base_cost = (
            10 * 100.0
            + 10 * 20.0
            + 800.0
            + 1500.0
            + 180.0
            + 120.0
        )

        expected_unmapped_auxiliary_cost = (
            5.0 * evaluation.panel_count
            + 50.0 * evaluation.installed_power_kwp
            + 10.0
            * evaluation.panel_count
            * selection.panel.area_m2
        )

        expected_installation_cost = (
            expected_base_cost
            + expected_unmapped_auxiliary_cost
        )

        assert costs.calculate_installation_cost(
            evaluation
        ) == pytest.approx(expected_installation_cost)

        assert costs.calculate_legalization_cost(
            evaluation
        ) == pytest.approx(650.0)


    def test_legalization_is_included_in_economic_configuration(
        self,
        selection: InstallationComponentSelection,
        evaluation: InstallationEvaluation,
    ) -> None:
        costs = self._build_costs(selection)

        economic = costs.build_economic_configuration(evaluation)

        assert economic.installation_cost_eur == pytest.approx(
            costs.calculate_installation_cost(evaluation) + 650.0
        )
        assert economic.battery_cost_eur == 0.0

    def test_from_selection_rejects_invalid_selection_type(self) -> None:
        with pytest.raises(TypeError):
            InstallationCostConfiguration.from_selection(object())

    def test_installation_cost_includes_unmapped_per_panel_cost_once(
        self,
        selection: InstallationComponentSelection,
        evaluation: InstallationEvaluation,
    ) -> None:
        costs = self._build_costs(selection)

        base_cost_without_auxiliary = (
            costs.calculate_panel_cost(evaluation.panel_count)
            + costs.calculate_structure_cost(evaluation)
            + costs.calculate_installation_service_cost(evaluation)
            + costs.calculate_inverter_cost(evaluation)
            + costs.calculate_electrical_protection_cost(evaluation)
            + costs.calculate_cabling_cost(evaluation)
        )

        # Los auxiliares variables aún no están incorporados
        # en las categorías tradicionales.
        expected_auxiliary = (
            5.0 * evaluation.panel_count
            + 50.0 * evaluation.installed_power_kwp
            + 10.0
            * evaluation.panel_count
            * selection.panel.area_m2
        )

        assert costs.calculate_installation_cost(
            evaluation
        ) == pytest.approx(
            base_cost_without_auxiliary + expected_auxiliary
        )

    def test_unmapped_per_kwp_cost_uses_installed_power(
        self,
        selection: InstallationComponentSelection,
        evaluation: InstallationEvaluation,
    ) -> None:
        costs = self._build_costs(selection)

        expected = (
            5.0 * evaluation.panel_count
            + 50.0 * evaluation.installed_power_kwp
            + 10.0
            * evaluation.panel_count
            * selection.panel.area_m2
        )

        assert costs.calculate_unmapped_auxiliary_cost(
            evaluation
        ) == pytest.approx(expected)

    def test_unmapped_per_m2_cost_uses_selected_panel_area(
        self,
        selection: InstallationComponentSelection,
        evaluation: InstallationEvaluation,
    ) -> None:
        costs = self._build_costs(selection)

        expected_area_cost = (
            10.0
            * evaluation.panel_count
            * selection.panel.area_m2
        )

        # Se comprueba el importe por superficie dentro del total
        # auxiliar no mapeado, descontando los otros dos conceptos.
        total_unmapped = costs.calculate_unmapped_auxiliary_cost(
            evaluation
        )

        expected_other_costs = (
            5.0 * evaluation.panel_count
            + 50.0 * evaluation.installed_power_kwp
        )

        assert total_unmapped - expected_other_costs == pytest.approx(
            expected_area_cost
        )

    def test_mapped_fixed_auxiliary_cost_is_not_counted_twice(
        self,
        selection: InstallationComponentSelection,
        evaluation: InstallationEvaluation,
    ) -> None:
        costs = self._build_costs(selection)

        assert costs.installation_cost_eur == pytest.approx(800.0)
        assert costs.calculate_unmapped_auxiliary_cost(
            evaluation
        ) == pytest.approx(
            5.0 * evaluation.panel_count
            + 50.0 * evaluation.installed_power_kwp
            + 10.0
            * evaluation.panel_count
            * selection.panel.area_m2
        )

    def test_legalization_is_excluded_from_base_but_included_economically(
        self,
        selection: InstallationComponentSelection,
        evaluation: InstallationEvaluation,
    ) -> None:
        costs = self._build_costs(selection)

        base_cost = costs.calculate_installation_cost(evaluation)
        economic = costs.build_economic_configuration(evaluation)

        assert costs.calculate_legalization_cost(
            evaluation
        ) == pytest.approx(650.0)

        assert economic.installation_cost_eur == pytest.approx(
            base_cost + 650.0
        )

    def test_initial_economic_configuration_excludes_battery_cost(
        self,
        selection: InstallationComponentSelection,
        evaluation: InstallationEvaluation,
    ) -> None:
        costs = self._build_costs(selection)

        economic = costs.build_economic_configuration(evaluation)

        assert selection.battery.price_eur == pytest.approx(2000.0)
        assert economic.battery_cost_eur == pytest.approx(0.0)

    def test_catalog_selection_costs_reach_coordinator_economic_configuration(
        self,
        selection: InstallationComponentSelection,
        evaluation: InstallationEvaluation,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        installation_configuration = InstallationConfiguration(
            available_area_m2=42.25,
            panel_width_m=1.134,
            panel_height_m=1.762,
            panel_power_wp=540,
            min_panels=5,
            max_panels=15,
            maintenance_passage_required=False,
            maintenance_passage_width_m=0.45,
            maintenance_passage_orientation="auto",
        )

        optimizer = InstallationOptimizer(
            installation_configuration.to_constraints()
        )
        evaluator = InstallationEvaluator(
            installation_configuration.to_constraints()
        )
        energy_recommender = EnergyRecommender()

        captured: dict = {}

        def fake_recommend(**kwargs):
            captured.update(kwargs)
            return object()

        monkeypatch.setattr(
            energy_recommender,
            "recommend",
            fake_recommend,
        )

        coordinator = InstallationCoordinator(
            optimizer=optimizer,
            evaluator=evaluator,
            recommender=InstallationRecommender(),
            production_calculator=lambda candidate: SolarProductionProfile(
                hourly_production=pd.Series(
                    1.0,
                    index=pd.date_range(
                        "2025-01-01",
                        periods=8760,
                        freq="h",
                    ),
                    name="production_kwh",
                ),
                reference_year=2025,
                installed_power_kwp=(
                    candidate.panel_count
                    * candidate.panel_power_wp
                    / 1000.0
                ),
            ),
            energy_recommender=energy_recommender,
        )

        profile = SolarProductionProfile(
            hourly_production=pd.Series(
                1.0,
                index=pd.date_range(
                    "2025-01-01",
                    periods=8760,
                    freq="h",
                ),
                name="production_kwh",
            ),
            reference_year=2025,
            installed_power_kwp=evaluation.installed_power_kwp,
        )

        monkeypatch.setattr(
            coordinator,
            "_generate_evaluations",
            lambda: [evaluation],
        )
        monkeypatch.setattr(
            coordinator,
            "_calculate_productions",
            lambda evaluations: {
                evaluation.panel_count: profile,
            },
        )

        costs = InstallationCostConfiguration.from_selection(
            selection,
            auxiliary_cost_categories={
                "installation": "installation",
                "protections": "electrical_protection",
                "cabling": "cabling",
                "legalization": "legalization",
            },
        )

        coordinator.recommend_energy(
            configuration=installation_configuration,
            annual_consumption_kwh=8760.0,
            consumption_scenario=object.__new__(ConsumptionScenario),
            candidate_capacities_kwh=[5.0, 8.3],
            max_charge_power_kw=5.0,
            max_discharge_power_kw=5.0,
            installation_cost_configuration=costs,
        )

        economic_factory = captured["economic_configuration_factory"]
        economic = economic_factory(evaluation, profile)

        expected_base_cost = (
            10 * 100.0                 # Paneles
            + 10 * 20.0                # Estructura
            + 800.0                    # Mano de obra
            + 1500.0                   # Inversor
            + 180.0                    # Protecciones
            + 120.0                    # Cableado
            + 5.0 * 10                  # Auxiliar por panel
            + 50.0 * 5.4               # Auxiliar por kWp
            + 10.0 * 10 * selection.panel.area_m2  # Auxiliar por m²
        )

        expected_total = expected_base_cost + 650.0  # Legalización

        assert economic.installation_cost_eur == pytest.approx(
            expected_total
        )
        assert economic.battery_cost_eur == pytest.approx(0.0)
        assert economic.annual_pv_savings_eur == pytest.approx(0.0)

        # La fábrica llega al recomendador y la batería se deja fuera
        # del coste inicial de instalación.
        assert callable(economic_factory)
        assert captured["battery_cost_per_kwh_eur"] == pytest.approx(249.70)

    
    def test_catalog_installation_cost_and_battery_cost_reach_combined_optimizer(
        self,
        selection,
        evaluation,
        monkeypatch,
    ):
        import pandas as pd

        from helios.core.consumption_scenario import (
            ConsumptionScenario,
        )
        from helios.solar.battery_economic_model import (
            BatteryEconomicModel,
        )
        from helios.solar.battery_optimizer import BatteryOptimizer
        from helios.solar.production_profile import (
            SolarProductionProfile,
        )

        costs = self._build_costs(selection)

        economic_configuration = (
            costs.build_economic_configuration(evaluation)
        )

        expected_installation_cost = (
            10 * 100.0
            + 10 * 20.0
            + 800.0
            + 1500.0
            + 180.0
            + 120.0
            + 10 * 5.0
            + 5.4 * 50.0
            + 10 * 10.0 * selection.panel.area_m2
            + 650.0
        )

        assert economic_configuration.installation_cost_eur == pytest.approx(
            expected_installation_cost
        )
        assert economic_configuration.battery_cost_eur == pytest.approx(0.0)

        index = pd.date_range(
            start="2025-01-01",
            periods=8760,
            freq="h",
        )

        consumption = ConsumptionScenario(
            hourly_consumption=pd.Series(
                [1.0] * 8760,
                index=index,
                dtype=float,
            )
        )

        production = SolarProductionProfile(
            hourly_production=pd.Series(
                [1.0] * 8760,
                index=index,
                dtype=float,
            ),
            reference_year=2025,
            installed_power_kwp=5.4,
        )

        original_calculate_combined = (
            BatteryEconomicModel.calculate_combined
        )
        received_configurations = []

        def capture_combined_configuration(
            model,
            configuration,
        ):
            received_configurations.append(configuration)
            return original_calculate_combined(
                model,
                configuration,
            )

        monkeypatch.setattr(
            BatteryEconomicModel,
            "calculate_combined",
            capture_combined_configuration,
        )

        recommendations = BatteryOptimizer().evaluate(
            consumption_scenario=consumption,
            production_profile=production,
            candidate_capacities_kwh=[5.0, 8.3],
            max_charge_power_kw=5.0,
            max_discharge_power_kw=5.0,
            combined_economic_configuration=economic_configuration,
        )

        assert len(recommendations) == 2
        assert len(received_configurations) == 2

        for capacity_kwh, configuration in zip(
            (5.0, 8.3),
            received_configurations,
            strict=True,
        ):
            expected_battery_cost = capacity_kwh * 249.70

            assert configuration.installation_cost_eur == pytest.approx(
                expected_installation_cost
            )
            assert configuration.battery_cost_eur == pytest.approx(
                expected_battery_cost
            )

        assert economic_configuration.installation_cost_eur == pytest.approx(
            expected_installation_cost
        )
        assert economic_configuration.battery_cost_eur == pytest.approx(0.0)