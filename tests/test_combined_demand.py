import pandas as pd
import pytest

from helios.core.combined_demand import CombinedDemandBuilder
from helios.core.consumption_scenario import ConsumptionScenario
from helios.ev.scenario import EVScenario


def create_index(reference_year=2025):
    return pd.date_range(
        f"{reference_year}-01-01 00:00:00",
        periods=8760,
        freq="h",
    )


def create_consumption_scenario(
    value=2.0,
    reference_year=2025,
):
    index = create_index(reference_year)

    return ConsumptionScenario(
        hourly_consumption=pd.Series(
            value,
            index=index,
            dtype=float,
        ),
        reference_year=reference_year,
    )


def create_ev_scenario(
    value=1.0,
    reference_year=2025,
):
    index = create_index(reference_year)

    return EVScenario(
        hourly_consumption=pd.Series(
            value,
            index=index,
            dtype=float,
        ),
        reference_year=reference_year,
    )


def test_combined_demand_returns_consumption_scenario():
    consumption = create_consumption_scenario()
    ev = create_ev_scenario()

    result = CombinedDemandBuilder.build(
        consumption,
        ev,
    )

    assert isinstance(result, ConsumptionScenario)
    assert result.reference_year == 2025


def test_combined_demand_sums_hourly_consumption():
    consumption = create_consumption_scenario(2.0)
    ev = create_ev_scenario(1.0)

    result = CombinedDemandBuilder.build(
        consumption,
        ev,
    )

    assert (result.hourly_consumption == 3.0).all()
    assert result.annual_consumption == pytest.approx(
        8760.0 * 3.0
    )


def test_combined_demand_preserves_hourly_index():
    consumption = create_consumption_scenario()
    ev = create_ev_scenario()

    result = CombinedDemandBuilder.build(
        consumption,
        ev,
    )

    assert result.hourly_consumption.index.equals(
        consumption.hourly_consumption.index
    )


def test_combined_demand_does_not_modify_original_scenarios():
    consumption = create_consumption_scenario(2.0)
    ev = create_ev_scenario(1.0)

    original_consumption = consumption.hourly_consumption.copy()
    original_ev = ev.hourly_consumption.copy()

    CombinedDemandBuilder.build(
        consumption,
        ev,
    )

    assert consumption.hourly_consumption.equals(
        original_consumption
    )
    assert ev.hourly_consumption.equals(
        original_ev
    )


def test_combined_demand_handles_variable_hourly_profiles():
    index = create_index()

    consumption_values = pd.Series(
        0.0,
        index=index,
        dtype=float,
    )
    ev_values = pd.Series(
        0.0,
        index=index,
        dtype=float,
    )

    consumption_values.iloc[100] = 4.5
    ev_values.iloc[100] = 2.5

    consumption = ConsumptionScenario(
        hourly_consumption=consumption_values,
        reference_year=2025,
    )

    ev = EVScenario(
        hourly_consumption=ev_values,
        reference_year=2025,
    )

    result = CombinedDemandBuilder.build(
        consumption,
        ev,
    )

    assert result.hourly_consumption.iloc[100] == pytest.approx(7.0)
    assert result.hourly_consumption.sum() == pytest.approx(7.0)


def test_combined_demand_rejects_invalid_consumption_scenario():
    ev = create_ev_scenario()

    with pytest.raises(
        TypeError,
        match="consumption_scenario",
    ):
        CombinedDemandBuilder.build(
            object(),
            ev,
        )


def test_combined_demand_rejects_invalid_ev_scenario():
    consumption = create_consumption_scenario()

    with pytest.raises(
        TypeError,
        match="ev_scenario",
    ):
        CombinedDemandBuilder.build(
            consumption,
            object(),
        )

def test_combined_demand_requires_same_hourly_index():
    consumption = create_consumption_scenario(
        reference_year=2025,
    )

    ev_index = create_index(reference_year=2025)

    # Mantener un índice válido para EVScenario pero distinto
    # del escenario de consumo.
    ev_index = ev_index.copy()
    ev_index = ev_index.rename("ev")

    ev = EVScenario(
        hourly_consumption=pd.Series(
            1.0,
            index=ev_index,
        ),
        reference_year=2025,
    )

    # El nombre del índice no forma parte de DatetimeIndex.equals(),
    # por lo que ambos índices siguen siendo iguales. Para probar
    # realmente el contrato necesitamos una diferencia que no rompa
    # la validez del EVScenario.
    #
    # En este diseño los dos escenarios con el mismo reference_year
    # están obligados a tener exactamente el mismo índice. Por tanto,
    # esta validación es inalcanzable mediante dos EV/ConsumptionScenario
    # válidos y no debe formar parte de este test.
    assert ev.hourly_consumption.index.equals(
        consumption.hourly_consumption.index
    )

def test_combined_demand_preserves_energy_conservation():
    consumption = create_consumption_scenario(2.75)
    ev = create_ev_scenario(0.35)

    result = CombinedDemandBuilder.build(
        consumption,
        ev,
    )

    assert result.annual_consumption == pytest.approx(
        consumption.annual_consumption
        + ev.annual_consumption
    )