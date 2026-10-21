from helios.core.analyzer import ConsumptionAnalyzer
from helios.core.economics_configuration import EconomicsConfiguration
from helios.core.tariffs_model import TariffPrices

from helios.solar.configuration import SolarConfiguration
from helios.solar.battery_configuration import BatteryConfiguration
from helios.solar.installation_costs import InstallationCostConfiguration

from helios.ev.configuration import EVConfiguration
from helios.ev.builder import EVScenarioBuilder
from helios.ev.scenario import EVScenario

from helios.solar.components_catalog import ComponentCatalog
from helios.solar.installation_component_selection import (
    InstallationComponentSelection,
)

class HeliosProject:

    def __init__(
        self,
        economics_configuration: EconomicsConfiguration
    ):

        self.analyzer = ConsumptionAnalyzer(
            economics_configuration
        )

        # Presupuesto cerrado de la instalación FV, sin baterías.
        # Se conserva separado de la inversión total, que puede
        # actualizarse posteriormente al recomendar una batería.
        self.closed_installation_cost_eur = float(
            economics_configuration.installation_cost
        )

        self.analyzer.project = self

        self.tariff_prices = TariffPrices()

        self.solar_configuration: SolarConfiguration | None = None

        self.battery_configuration: BatteryConfiguration | None = None

        self.installation_cost_configuration: InstallationCostConfiguration | None = None

        self.ev_configuration: EVConfiguration | None = None

        self.component_catalog: ComponentCatalog | None = None

        self.component_selection: InstallationComponentSelection | None = None

    # ==================================================
    # Controllers
    # ==================================================

    @property
    def validation(self):
        return self.analyzer.validation

    @property
    def statistics(self):
        return self.analyzer.statistics

    @property
    def profiles(self):
        return self.analyzer.profiles

    @property
    def comparisons(self):
        return self.analyzer.comparisons

    @property
    def indicators(self):
        return self.analyzer.indicators

    @property
    def tariffs(self):
        return self.analyzer.tariffs

    @property
    def solar(self):
        return self.analyzer.solar

    @property
    def economics(self):
        return self.analyzer.economics

    @property
    def dataset(self):
        return self.analyzer.dataset

    @property
    def quality(self):
        return self.analyzer.quality

    # ==================================================
    # Configuración solar
    # ==================================================

    def set_solar_configuration(
        self,
        configuration: SolarConfiguration,
    ):
        
        self.solar_configuration = configuration
        self.solar.set_configuration(configuration)

    def set_installation_cost_configuration(
        self,
        configuration: InstallationCostConfiguration,
    ) -> None:

        if not isinstance(
            configuration,
            InstallationCostConfiguration,
        ):
            raise TypeError(
                "configuration must be an InstallationCostConfiguration."
            )

        self.installation_cost_configuration = configuration

    def set_battery_configuration(
        self,
        configuration: BatteryConfiguration,
    ) -> None:
        
        self.battery_configuration = configuration
        self.solar.invalidate_energy_balance()

    def set_ev_configuration(
        self,
        configuration: EVConfiguration,
    ) -> None:

        self.ev_configuration = configuration
        self.solar.invalidate_energy_balance()

    def build_ev_scenario(self) -> EVScenario:
        if self.ev_configuration is None:
            raise ValueError(
                "EV configuration has not been set."
            )

        return EVScenarioBuilder.build(
            self.ev_configuration
        )

    # ==================================================
    # Carga y preparación de datos
    # ==================================================

    def load_data(self, path):

        self.analyzer.load_excel(path)
        self.analyzer.clean_data()
        self.analyzer.build_datetime()

    def analyze_data(self):

        self.analyzer.validation.calculate()
        self.analyzer.statistics.calculate()
        self.analyzer.profiles.calculate()
        self.analyzer.comparisons.calculate()
        self.analyzer.indicators.calculate()
        self.analyzer.tariffs.calculate()

    def set_component_catalog(
        self,
        catalog: ComponentCatalog,
    ) -> None:
        """Configura el catálogo de componentes disponibles."""
        if not isinstance(catalog, ComponentCatalog):
            raise TypeError(
                "catalog debe ser una instancia de ComponentCatalog."
            )

        if (
            self.component_selection is not None
            and self.component_selection.catalog is not catalog
        ):
            raise ValueError(
                "No se puede sustituir el catálogo mientras exista "
                "una selección vinculada a otro catálogo. "
                "Limpia primero la selección."
            )

        self.component_catalog = catalog


    def set_component_selection(
        self,
        selection: InstallationComponentSelection | None,
    ) -> None:
        """Configura o limpia la selección de componentes."""
        if selection is None:
            self.component_selection = None
            return

        if not isinstance(selection, InstallationComponentSelection):
            raise TypeError(
                "selection debe ser una instancia de "
                "InstallationComponentSelection o None."
            )

        if self.component_catalog is None:
            raise ValueError(
                "Debes configurar el catálogo antes de seleccionar "
                "componentes."
            )

        if selection.catalog is not self.component_catalog:
            raise ValueError(
                "La selección debe pertenecer al catálogo del proyecto."
            )

        self.component_selection = selection