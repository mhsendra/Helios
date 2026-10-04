import pytest

from helios.core.diagnostics import (
    DiagnosticResult,
    EnergyRecommendations,
    RecommendationResult,
)

from helios.core.diagnostics.battery_economics import (
    BatteryEconomicAnalyzer,
    BatteryEconomicRecommendation,
)

def _diagnostic(
    code: str,
    evidence: dict[str, float | str],
) -> DiagnosticResult:
    return DiagnosticResult(
        code=code,
        category="energy",
        severity="warning",
        title=f"Diagnostic {code}",
        description="Diagnostic description.",
        evidence=evidence,
    )


def test_recommend_empty_when_there_are_no_diagnostics():
    assert EnergyRecommendations.recommend([]) == []


def test_recommend_storage_when_surplus_and_hourly_mismatch_exist():
    diagnostics = [
        _diagnostic(
            "HIGH_SOLAR_SURPLUS",
            {
                "production_kwh": 12000.0,
                "grid_export_kwh": 8000.0,
                "export_ratio_percent": 66.67,
            },
        ),
        _diagnostic(
            "HIGH_HOURLY_MISMATCH",
            {
                "excess_energy_kwh": 8000.0,
                "deficit_energy_kwh": 12000.0,
                "excess_ratio_percent": 66.67,
                "deficit_ratio_percent": 61.54,
                "production_consumption_overlap_ratio_percent": 38.46,
            },
        ),
    ]

    recommendations = EnergyRecommendations.recommend(diagnostics)

    assert len(recommendations) == 1

    recommendation = recommendations[0]

    assert isinstance(recommendation, RecommendationResult)
    assert recommendation.code == "CONSIDER_ENERGY_STORAGE"
    assert recommendation.supporting_diagnostics == (
        "HIGH_SOLAR_SURPLUS",
        "HIGH_HOURLY_MISMATCH",
    )
    assert recommendation.evidence["export_ratio_percent"] == 66.67
    assert recommendation.evidence["excess_energy_kwh"] == 8000.0
    assert recommendation.evidence["deficit_energy_kwh"] == 12000.0


def test_recommend_self_consumption_improvement_for_surplus_only():
    diagnostics = [
        _diagnostic(
            "HIGH_SOLAR_SURPLUS",
            {
                "production_kwh": 12000.0,
                "grid_export_kwh": 8000.0,
                "export_ratio_percent": 66.67,
            },
        ),
    ]

    recommendations = EnergyRecommendations.recommend(diagnostics)

    assert len(recommendations) == 1
    assert recommendations[0].code == (
        "CONSIDER_SELF_CONSUMPTION_IMPROVEMENT"
    )
    assert recommendations[0].supporting_diagnostics == (
        "HIGH_SOLAR_SURPLUS",
    )


def test_recommend_grid_dependence_review():
    diagnostics = [
        _diagnostic(
            "HIGH_GRID_DEPENDENCE",
            {
                "consumption_kwh": 19000.0,
                "grid_import_kwh": 11000.0,
                "grid_import_ratio_percent": 57.89,
            },
        ),
    ]

    recommendations = EnergyRecommendations.recommend(diagnostics)

    assert len(recommendations) == 1
    assert recommendations[0].code == "REVIEW_GRID_DEPENDENCE"
    assert recommendations[0].supporting_diagnostics == (
        "HIGH_GRID_DEPENDENCE",
    )
    assert recommendations[0].evidence["grid_import_kwh"] == 11000.0


def test_recommend_storage_and_grid_review_can_coexist():
    diagnostics = [
        _diagnostic(
            "HIGH_SOLAR_SURPLUS",
            {
                "production_kwh": 12000.0,
                "grid_export_kwh": 8000.0,
                "export_ratio_percent": 66.67,
            },
        ),
        _diagnostic(
            "HIGH_HOURLY_MISMATCH",
            {
                "excess_energy_kwh": 8000.0,
                "deficit_energy_kwh": 12000.0,
                "excess_ratio_percent": 66.67,
                "deficit_ratio_percent": 61.54,
                "production_consumption_overlap_ratio_percent": 38.46,
            },
        ),
        _diagnostic(
            "HIGH_GRID_DEPENDENCE",
            {
                "consumption_kwh": 19000.0,
                "grid_import_kwh": 11000.0,
                "grid_import_ratio_percent": 57.89,
            },
        ),
    ]

    recommendations = EnergyRecommendations.recommend(diagnostics)

    assert {item.code for item in recommendations} == {
        "CONSIDER_ENERGY_STORAGE",
        "REVIEW_GRID_DEPENDENCE",
    }


def test_recommendations_do_not_depend_on_diagnostic_order():
    diagnostics = [
        _diagnostic(
            "HIGH_HOURLY_MISMATCH",
            {
                "excess_energy_kwh": 8000.0,
                "deficit_energy_kwh": 12000.0,
                "excess_ratio_percent": 66.67,
                "deficit_ratio_percent": 61.54,
                "production_consumption_overlap_ratio_percent": 38.46,
            },
        ),
        _diagnostic(
            "HIGH_SOLAR_SURPLUS",
            {
                "production_kwh": 12000.0,
                "grid_export_kwh": 8000.0,
                "export_ratio_percent": 66.67,
            },
        ),
    ]

    recommendations = EnergyRecommendations.recommend(diagnostics)

    assert len(recommendations) == 1
    assert recommendations[0].code == "CONSIDER_ENERGY_STORAGE"


def test_recommendation_requires_supporting_diagnostic():
    with pytest.raises(ValueError, match="at least one diagnostic"):
        RecommendationResult(
            code="TEST",
            title="Test",
            description="Test",
            supporting_diagnostics=(),
            evidence={},
        )


def test_recommendation_requires_code():
    with pytest.raises(ValueError, match="code cannot be empty"):
        RecommendationResult(
            code="",
            title="Test",
            description="Test",
            supporting_diagnostics=("TEST",),
            evidence={},
        )


def test_recommendation_requires_title():
    with pytest.raises(ValueError, match="title cannot be empty"):
        RecommendationResult(
            code="TEST",
            title="",
            description="Test",
            supporting_diagnostics=("TEST",),
            evidence={},
        )


def test_recommendation_requires_description():
    with pytest.raises(
        ValueError,
        match="description cannot be empty",
    ):
        RecommendationResult(
            code="TEST",
            title="Test",
            description="",
            supporting_diagnostics=("TEST",),
            evidence={},
        )


def test_recommendation_is_immutable():
    recommendation = RecommendationResult(
        code="TEST",
        title="Test",
        description="Test",
        supporting_diagnostics=("TEST_DIAGNOSTIC",),
        evidence={"value": 1.0},
    )

    with pytest.raises(AttributeError):
        recommendation.code = "OTHER"

def test_energy_recommendations_enriches_storage_recommendation_with_positive_npv():
    diagnostics = [
        DiagnosticResult(
            code="HIGH_SOLAR_SURPLUS",
            category="energy",
            severity="warning",
            title="Alto excedente solar",
            description="Existe un excedente elevado.",
            evidence={
                "production_kwh": 12000.0,
                "grid_export_kwh": 8000.0,
                "export_ratio_percent": 66.67,
            },
        ),
        DiagnosticResult(
            code="HIGH_HOURLY_MISMATCH",
            category="energy",
            severity="info",
            title="Desajuste horario",
            description="Existe desajuste horario.",
            evidence={
                "excess_energy_kwh": 8000.0,
                "deficit_energy_kwh": 5000.0,
            },
        ),
    ]

    battery = BatteryEconomicRecommendation(
        capacity_kwh=8.3,
        criterion=BatteryEconomicAnalyzer.CRITERION_POSITIVE_NPV,
        title="Capacidad de batería económicamente óptima",
        description="La capacidad de 8.3 kWh presenta el mejor resultado.",
        evidence={
            "capacity_kwh": 8.3,
            "economic_npv_eur": 1250.0,
            "economic_irr_percent": 8.5,
            "economic_payback_years": 11.2,
        },
    )

    recommendations = EnergyRecommendations.recommend(
        diagnostics,
        [battery],
    )

    storage = next(
        recommendation
        for recommendation in recommendations
        if recommendation.code == "CONSIDER_ENERGY_STORAGE"
    )

    assert storage.evidence["battery_capacity_kwh"] == 8.3
    assert storage.evidence["battery_economic_criterion"] == (
        BatteryEconomicAnalyzer.CRITERION_POSITIVE_NPV
    )
    assert storage.evidence["battery_economic_npv_eur"] == 1250.0
    assert "8.3 kWh" in storage.description

def test_energy_recommendations_distinguishes_technically_useful_but_economically_unviable_battery():
    diagnostics = [
        DiagnosticResult(
            code="HIGH_SOLAR_SURPLUS",
            category="energy",
            severity="warning",
            title="Alto excedente solar",
            description="Existe un excedente elevado.",
            evidence={
                "production_kwh": 12000.0,
                "grid_export_kwh": 8000.0,
                "export_ratio_percent": 66.67,
            },
        ),
        DiagnosticResult(
            code="HIGH_HOURLY_MISMATCH",
            category="energy",
            severity="info",
            title="Desajuste horario",
            description="Existe desajuste horario.",
            evidence={
                "excess_energy_kwh": 8000.0,
                "deficit_energy_kwh": 5000.0,
            },
        ),
    ]

    battery = BatteryEconomicRecommendation(
        capacity_kwh=8.3,
        criterion=BatteryEconomicAnalyzer.CRITERION_NO_POSITIVE_NPV,
        title="La batería no resulta económicamente viable",
        description=(
            "Ninguna de las capacidades evaluadas presenta "
            "un NPV incremental positivo."
        ),
        evidence={
            "capacity_kwh": 8.3,
            "economic_npv_eur": -1250.0,
            "economic_irr_percent": 1.5,
            "economic_payback_years": float("inf"),
        },
    )

    recommendations = EnergyRecommendations.recommend(
        diagnostics,
        [battery],
    )

    storage = next(
        recommendation
        for recommendation in recommendations
        if recommendation.code == "CONSIDER_ENERGY_STORAGE"
    )

    assert storage.evidence["battery_capacity_kwh"] == 8.3
    assert storage.evidence["battery_economic_criterion"] == (
        BatteryEconomicAnalyzer.CRITERION_NO_POSITIVE_NPV
    )
    assert storage.evidence["battery_economic_npv_eur"] == -1250.0
    assert (
        "ninguna de las capacidades evaluadas presenta"
        in storage.description.lower()
    )

def test_energy_recommendations_without_battery_economics_preserves_existing_behavior():
    diagnostics = [
        DiagnosticResult(
            code="HIGH_SOLAR_SURPLUS",
            category="energy",
            severity="warning",
            title="Alto excedente solar",
            description="Existe un excedente elevado.",
            evidence={
                "production_kwh": 12000.0,
                "grid_export_kwh": 8000.0,
                "export_ratio_percent": 66.67,
            },
        ),
        DiagnosticResult(
            code="HIGH_HOURLY_MISMATCH",
            category="energy",
            severity="info",
            title="Desajuste horario",
            description="Existe desajuste horario.",
            evidence={
                "excess_energy_kwh": 8000.0,
                "deficit_energy_kwh": 5000.0,
            },
        ),
    ]

    recommendations = EnergyRecommendations.recommend(diagnostics)

    storage = next(
        recommendation
        for recommendation in recommendations
        if recommendation.code == "CONSIDER_ENERGY_STORAGE"
    )

    assert "battery_capacity_kwh" not in storage.evidence
    assert "battery_economic_npv_eur" not in storage.evidence