import pytest

from helios.solar.battery_economic_model import (
    CombinedEconomicConfiguration,
)
from helios.solar.installation_costs import (
    InstallationCostConfiguration,
)


def test_calculate_panel_cost_uses_panel_count_and_unit_price():
    configuration = InstallationCostConfiguration(
        panel_unit_cost_eur=100.0,
    )

    assert configuration.calculate_panel_cost(5) == 500.0
    assert configuration.calculate_panel_cost(15) == 1500.0
    assert configuration.calculate_panel_cost(20) == 2000.0


def test_calculate_installation_cost_currently_equals_panel_cost():
    configuration = InstallationCostConfiguration(
        panel_unit_cost_eur=92.196,
    )

    assert configuration.calculate_installation_cost(15) == pytest.approx(
        1382.94,
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


def test_build_economic_configuration_returns_combined_configuration():
    configuration = InstallationCostConfiguration(
        panel_unit_cost_eur=100.0,
    )

    result = configuration.build_economic_configuration(
        panel_count=15,
    )

    assert isinstance(
        result,
        CombinedEconomicConfiguration,
    )

    assert result.installation_cost_eur == 1500.0
    assert result.battery_cost_eur == 0.0
    assert result.annual_pv_savings_eur == 0.0
    assert (
        result.annual_battery_additional_savings_eur
        == 0.0
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