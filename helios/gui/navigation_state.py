"""Reglas de acceso a las páginas de Helios."""

ANALYSIS_PAGES = frozenset({
    "Validación",
    "Estadísticas",
    "Perfiles",
    "Comparativas",
    "Indicadores",
    "Tarifas",
    "Gráficas",
})

ALL_PAGES = frozenset({
    "Configuración solar",
    "Cargar datos",
    "Optimización solar",
    "Solar",
    "Economía",
    "Informes",
}) | ANALYSIS_PAGES


def is_page_available(
    page_id: str,
    *,
    solar_configured: bool,
    project_loaded: bool,
    solar_optimized: bool,
    solar_production_calculated: bool,
    economics_calculated: bool,
) -> bool:
    """Determina el acceso sin consultar componentes visuales."""

    if page_id not in ALL_PAGES:
        return False

    if page_id == "Configuración solar":
        return True

    if page_id == "Cargar datos":
        return solar_configured

    if page_id == "Optimización solar":
        return project_loaded

    if page_id in ANALYSIS_PAGES:
        return project_loaded

    if page_id == "Solar":
        return solar_optimized

    if page_id == "Economía":
        return solar_optimized and solar_production_calculated

    if page_id == "Informes":
        return (
            solar_optimized
            and solar_production_calculated
            and economics_calculated
        )

    return False
