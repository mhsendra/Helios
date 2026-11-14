import pytest

from helios.gui.navigation_state import is_page_available


DEFAULT_STATE = {
    "solar_configured": False,
    "project_loaded": False,
    "solar_optimized": False,
    "solar_production_calculated": False,
    "economics_calculated": False,
}


@pytest.mark.parametrize(
    ("page_id", "changes", "expected"),
    [
        ("Configuración solar", {}, True),
        ("Cargar datos", {}, False),
        ("Cargar datos", {"solar_configured": True}, True),
        ("Optimización solar", {}, False),
        ("Optimización solar", {"project_loaded": True}, True),
        ("Validación", {"project_loaded": True}, True),
        ("Estadísticas", {"project_loaded": True}, True),
        ("Perfiles", {"project_loaded": True}, True),
        ("Comparativas", {"project_loaded": True}, True),
        ("Indicadores", {"project_loaded": True}, True),
        ("Tarifas", {"project_loaded": True}, True),
        ("Gráficas", {"project_loaded": True}, True),
        ("Solar", {}, False),
        ("Solar", {"solar_optimized": True}, True),
        ("Economía", {"solar_optimized": True}, False),
        (
            "Economía",
            {
                "solar_optimized": True,
                "solar_production_calculated": True,
            },
            True,
        ),
        (
            "Informes",
            {
                "solar_optimized": True,
                "solar_production_calculated": True,
            },
            False,
        ),
        (
            "Informes",
            {
                "solar_optimized": True,
                "solar_production_calculated": True,
                "economics_calculated": True,
            },
            True,
        ),
        ("Página inexistente", {}, False),
    ],
)
def test_page_availability(page_id, changes, expected):
    state = {**DEFAULT_STATE, **changes}

    assert is_page_available(page_id, **state) is expected
