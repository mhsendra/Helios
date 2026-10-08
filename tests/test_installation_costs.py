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
    [None, "20", True],
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