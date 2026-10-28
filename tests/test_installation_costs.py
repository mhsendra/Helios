import pytest

from helios.solar.battery_economic_model import (
    CombinedEconomicConfiguration,
)
from helios.solar.installation_candidate import (
    InstallationCandidate,
)
from helios.solar.installation_costs import (
    InstallationCostConfiguration,
)
from helios.solar.installation_evaluation import (
    InstallationEvaluation,
)
from helios.solar.installation_layout import (
    InstallationLayout,
)

from helios.solar.components_catalog import MountingSystemPackage

from helios.solar.default_component_catalog import (
    build_default_component_catalog,
)
from helios.solar.installation_component_selection import (
    InstallationComponentSelection,
)

def _evaluation(
    panel_count: int = 15,
    rows: int = 3,
    columns: int = 5,
) -> InstallationEvaluation:

    candidate = InstallationCandidate(
        panel_count=panel_count,
        panel_power_wp=540.0,
        panel_area_m2=2.58,
    )

    layout = InstallationLayout(
        rows=rows,
        columns=columns,
        panel_width_m=1.134,
        panel_height_m=2.278,
        orientation="vertical",
    )

    return InstallationEvaluation(
        candidate=candidate,
        available_area_m2=100.0,
        layout=layout,
    )


def test_calculate_panel_cost_uses_panel_count_and_unit_price():
    configuration = InstallationCostConfiguration(
        panel_unit_cost_eur=100.0,
    )

    assert configuration.calculate_panel_cost(5) == 500.0
    assert configuration.calculate_panel_cost(15) == 1500.0
    assert configuration.calculate_panel_cost(20) == 2000.0


def test_calculate_structure_cost_uses_evaluation():
    configuration = InstallationCostConfiguration(
        panel_unit_cost_eur=100.0,
        structure_unit_cost_eur=20.0,
    )

    evaluation = _evaluation(
        panel_count=15,
    )

    assert configuration.calculate_structure_cost(
        evaluation
    ) == 300.0


def test_calculate_structure_cost_accepts_different_layouts():
    configuration = InstallationCostConfiguration(
        panel_unit_cost_eur=100.0,
        structure_unit_cost_eur=20.0,
    )

    evaluation = _evaluation(
        panel_count=15,
        rows=5,
        columns=3,
    )

    assert configuration.calculate_structure_cost(
        evaluation
    ) == 300.0


def test_calculate_installation_cost_combines_panels_and_structure():
    configuration = InstallationCostConfiguration(
        panel_unit_cost_eur=100.0,
        structure_unit_cost_eur=20.0,
    )

    evaluation = _evaluation(
        panel_count=15,
    )

    assert configuration.calculate_installation_cost(
        evaluation
    ) == 1800.0


def test_build_economic_configuration_includes_structure():
    configuration = InstallationCostConfiguration(
        panel_unit_cost_eur=100.0,
        structure_unit_cost_eur=20.0,
    )

    result = configuration.build_economic_configuration(
        _evaluation(panel_count=15),
    )

    assert isinstance(
        result,
        CombinedEconomicConfiguration,
    )

    assert result.installation_cost_eur == 1800.0
    assert result.battery_cost_eur == 0.0
    assert result.annual_pv_savings_eur == 0.0
    assert (
        result.annual_battery_additional_savings_eur
        == 0.0
    )


@pytest.mark.parametrize(
    "panel_count",
    [1, 5, 10, 15, 16, 20, 50],
)
def test_panel_cost_scales_linearly_with_panel_count(
    panel_count,
):
    unit_price = 92.196

    configuration = InstallationCostConfiguration(
        panel_unit_cost_eur=unit_price,
    )

    assert configuration.calculate_panel_cost(
        panel_count,
    ) == pytest.approx(
        panel_count * unit_price,
    )


@pytest.mark.parametrize(
    "panel_count",
    [0, -1, -10],
)
def test_calculate_panel_cost_rejects_invalid_panel_count(
    panel_count,
):
    configuration = InstallationCostConfiguration(
        panel_unit_cost_eur=100.0,
    )

    with pytest.raises(
        ValueError,
        match="greater than zero",
    ):
        configuration.calculate_panel_cost(
            panel_count,
        )


@pytest.mark.parametrize(
    "panel_count",
    [1.5, "15", None, True],
)
def test_calculate_panel_cost_rejects_non_integer_panel_count(
    panel_count,
):
    configuration = InstallationCostConfiguration(
        panel_unit_cost_eur=100.0,
    )

    with pytest.raises(
        TypeError,
        match="integer",
    ):
        configuration.calculate_panel_cost(
            panel_count,
        )


@pytest.mark.parametrize(
    "unit_price",
    [-1.0, -100.0],
)
def test_configuration_rejects_negative_panel_price(
    unit_price,
):
    with pytest.raises(
        ValueError,
        match="cannot be negative",
    ):
        InstallationCostConfiguration(
            panel_unit_cost_eur=unit_price,
        )


@pytest.mark.parametrize(
    "unit_price",
    [None, "100", True],
)
def test_configuration_rejects_invalid_panel_price(
    unit_price,
):
    with pytest.raises(
        TypeError,
        match="numeric",
    ):
        InstallationCostConfiguration(
            panel_unit_cost_eur=unit_price,
        )


@pytest.mark.parametrize(
    "unit_price",
    [-1.0, -100.0],
)
def test_configuration_rejects_negative_structure_price(
    unit_price,
):
    with pytest.raises(
        ValueError,
        match="cannot be negative",
    ):
        InstallationCostConfiguration(
            panel_unit_cost_eur=100.0,
            structure_unit_cost_eur=unit_price,
        )


@pytest.mark.parametrize(
    "unit_price",
    ["20", True],
)
def test_configuration_rejects_invalid_structure_price(
    unit_price,
):
    with pytest.raises(
        TypeError,
        match="numeric",
    ):
        InstallationCostConfiguration(
            panel_unit_cost_eur=100.0,
            structure_unit_cost_eur=unit_price,
        )


def test_configuration_accepts_unknown_structure_price():
    configuration = InstallationCostConfiguration(
        panel_unit_cost_eur=100.0,
        structure_unit_cost_eur=None,
    )

    assert configuration.structure_unit_cost_eur is None


@pytest.mark.parametrize(
    "calculate",
    [
        "calculate_structure_cost",
        "calculate_installation_cost",
        "build_economic_configuration",
    ],
)
def test_unknown_structure_cost_blocks_economic_calculation(
    calculate,
):
    configuration = InstallationCostConfiguration(
        panel_unit_cost_eur=100.0,
        structure_unit_cost_eur=None,
    )
    evaluation = _evaluation(panel_count=15)

    with pytest.raises(
        ValueError,
        match="coste de la estructura no está confirmado",
    ):
        getattr(configuration, calculate)(evaluation)


def test_unknown_structure_cost_allows_matching_package():
    configuration = InstallationCostConfiguration(
        panel_unit_cost_eur=100.0,
        structure_unit_cost_eur=None,
        structure_package_cost_eur=392.27,
        structure_package_panel_count=15,
    )

    assert configuration.calculate_structure_cost(
        _evaluation(panel_count=15),
    ) == pytest.approx(392.27)

def test_unknown_structure_cost_rejects_non_matching_package():
    configuration = InstallationCostConfiguration(
        panel_unit_cost_eur=100.0,
        structure_unit_cost_eur=None,
        structure_package_cost_eur=392.27,
        structure_package_panel_count=16,
    )

    with pytest.raises(
        ValueError,
        match="coste de la estructura no está confirmado",
    ):
        configuration.calculate_structure_cost(
            _evaluation(panel_count=15),
        )


@pytest.mark.parametrize(
    "evaluation",
    [None, "evaluation", 15, True],
)
def test_structure_cost_rejects_invalid_evaluation(
    evaluation,
):
    configuration = InstallationCostConfiguration(
        panel_unit_cost_eur=100.0,
        structure_unit_cost_eur=20.0,
    )

    with pytest.raises(
        TypeError,
        match="InstallationEvaluation",
    ):
        configuration.calculate_structure_cost(
            evaluation
        )

def test_inverter_cost_is_fixed():
    evaluation_15 = _evaluation(panel_count=15)
    evaluation_10 = _evaluation(
        panel_count=10,
        rows=2,
        columns=5,
    )

    configuration = InstallationCostConfiguration(
        panel_unit_cost_eur=100.0,
        structure_unit_cost_eur=20.0,
        installation_cost_eur=2950.0,
        inverter_unit_cost_eur=1200.0,
    )

    assert (
        configuration.calculate_inverter_cost(
            evaluation_15
        )
        == 1200.0
    )

    assert (
        configuration.calculate_inverter_cost(
            evaluation_10
        )
        == 1200.0
    )

def test_electrical_protection_cost_is_fixed():
    evaluation = _evaluation(panel_count=15)

    configuration = InstallationCostConfiguration(
        panel_unit_cost_eur=100.0,
        electrical_protection_cost_eur=450.0,
    )

    assert (
        configuration.calculate_electrical_protection_cost(
            evaluation
        )
        == 450.0
    )

def test_cabling_cost_is_fixed():
    evaluation = _evaluation(panel_count=15)

    configuration = InstallationCostConfiguration(
        panel_unit_cost_eur=100.0,
        cabling_cost_eur=600.0,
    )

    assert (
        configuration.calculate_cabling_cost(
            evaluation
        )
        == 600.0
    )

def test_legalization_cost_is_fixed():
    evaluation = _evaluation(panel_count=15)

    configuration = InstallationCostConfiguration(
        panel_unit_cost_eur=100.0,
        legalization_cost_eur=650.0,
    )

    assert (
        configuration.calculate_legalization_cost(
            evaluation
        )
        == 650.0
    )

def test_legalization_cost_is_not_part_of_installation_cost():
    evaluation = _evaluation(panel_count=15)

    configuration = InstallationCostConfiguration(
        panel_unit_cost_eur=100.0,
        structure_unit_cost_eur=20.0,
        installation_cost_eur=2950.0,
        inverter_unit_cost_eur=1200.0,
        electrical_protection_cost_eur=450.0,
        cabling_cost_eur=600.0,
        legalization_cost_eur=650.0,
    )

    installation_cost = (
        configuration.calculate_installation_cost(
            evaluation
        )
    )

    assert installation_cost == (
        1500.0
        + 300.0
        + 2950.0
        + 1200.0
        + 450.0
        + 600.0
    )

def test_legalization_cost_is_included_in_economic_configuration():
    evaluation = _evaluation(panel_count=15)

    configuration = InstallationCostConfiguration(
        panel_unit_cost_eur=100.0,
        legalization_cost_eur=650.0,
    )

    economic = (
        configuration.build_economic_configuration(
            evaluation
        )
    )

    assert economic.installation_cost_eur == (
        1500.0 + 650.0
    )

@pytest.mark.parametrize(
    "field_name",
    [
        "panel_unit_cost_eur",
        "structure_unit_cost_eur",
        "installation_cost_eur",
        "inverter_unit_cost_eur",
        "electrical_protection_cost_eur",
        "cabling_cost_eur",
        "legalization_cost_eur",
    ],
)
@pytest.mark.parametrize(
    "invalid_value",
    [
        float("nan"),
        float("inf"),
        float("-inf"),
    ],
)
def test_configuration_rejects_non_finite_costs(
    field_name,
    invalid_value,
):
    values = {
        "panel_unit_cost_eur": 100.0,
    }
    values[field_name] = invalid_value

    with pytest.raises(
        ValueError,
        match="must be finite",
    ):
        InstallationCostConfiguration(**values)


def test_from_selection_maps_cabling_and_protection_costs_once():
    catalog = build_default_component_catalog()

    selection = InstallationComponentSelection(
        catalog=catalog,
        panel_id="longi lr7-60hvh-540m",
        inverter_id="goodwe-gw8k-eha-g20",
        mounting_system_id=None,
        roof_type="tile",
        auxiliary_cost_ids=tuple(
            item.id for item in catalog.auxiliary_costs
        ),
    )

    categories = {
        "electrical_protection_dc": "electrical_protection",
        "electrical_protection_ac": "electrical_protection",
        "solar_cabling_red": "cabling",
        "solar_cabling_black": "cabling",
        "connector_female": "cabling",
        "connector_male": "cabling",
        "joining_profiles": "cabling",
        "installation": "installation",
        "legalization_estimate": "legalization",
    }

    configuration = InstallationCostConfiguration.from_selection(
        selection,
        auxiliary_cost_categories=categories,
    )

    assert configuration.cabling_cost_eur == pytest.approx(
        110.58 + 14.78 + 14.18 + 8.27
    )
    assert configuration.electrical_protection_cost_eur == pytest.approx(
        343.962
    )
    assert configuration.installation_cost_eur == pytest.approx(
        2950.0
    )
    assert configuration.legalization_cost_eur == pytest.approx(
        650.0
    )

    evaluation = _evaluation(panel_count=15)

    assert configuration.calculate_unmapped_auxiliary_cost(
        evaluation
    ) == pytest.approx(0.0)

def test_dynamic_structure_cost_uses_cheapest_mounting_packages():
    packages = (
        MountingSystemPackage(
            id="kit-1",
            mounting_system_id="sunfer-test",
            model="Kit 1 panel",
            panel_capacity=1,
            quantity=1,
            unit_price_eur=60.0,
        ),
        MountingSystemPackage(
            id="kit-2",
            mounting_system_id="sunfer-test",
            model="Kit 2 paneles",
            panel_capacity=2,
            quantity=1,
            unit_price_eur=90.0,
        ),
        MountingSystemPackage(
            id="kit-3",
            mounting_system_id="sunfer-test",
            model="Kit 3 paneles",
            panel_capacity=3,
            quantity=1,
            unit_price_eur=110.0,
        ),
        MountingSystemPackage(
            id="kit-5",
            mounting_system_id="sunfer-test",
            model="Kit 5 paneles",
            panel_capacity=5,
            quantity=1,
            unit_price_eur=150.0,
        ),
    )

    configuration = InstallationCostConfiguration(
        panel_unit_cost_eur=100.0,
        structure_unit_cost_eur=None,
        mounting_packages=packages,
        mounting_system_id="sunfer-test",
    )

    assert configuration.calculate_structure_cost(
        _evaluation(panel_count=15, rows=3, columns=5),
    ) == pytest.approx(450.0)


def test_dynamic_structure_cost_splits_vertical_walkway():
    packages = (
        MountingSystemPackage(
            id="kit-2",
            mounting_system_id="sunfer-test",
            model="Kit 2 paneles",
            panel_capacity=2,
            quantity=1,
            unit_price_eur=90.0,
        ),
        MountingSystemPackage(
            id="kit-3",
            mounting_system_id="sunfer-test",
            model="Kit 3 paneles",
            panel_capacity=3,
            quantity=1,
            unit_price_eur=110.0,
        ),
    )

    layout = InstallationLayout(
        rows=3,
        columns=5,
        panel_width_m=1.134,
        panel_height_m=2.278,
        orientation="vertical",
        walkway_width_m=0.5,
        walkway_position="vertical",
    )

    candidate = InstallationCandidate(
        panel_count=15,
        panel_power_wp=540.0,
        panel_area_m2=2.58,
    )

    evaluation = InstallationEvaluation(
        candidate=candidate,
        available_area_m2=100.0,
        layout=layout,
    )

    configuration = InstallationCostConfiguration(
        panel_unit_cost_eur=100.0,
        structure_unit_cost_eur=None,
        mounting_packages=packages,
        mounting_system_id="sunfer-test",
    )

    # Cada fila se divide en dos tramos: 2 + 3 paneles.
    assert configuration.calculate_structure_cost(
        evaluation,
    ) == pytest.approx(600.0)