class SolarManager:

    def __init__(self):

        self.production_engine = SolarProductionEngine()

        self.balance_engine = EnergyBalanceEngine()

        self.statistics_engine = SolarStatisticsEngine()

        self.configuration = None

        self.hourly_production = None

        self.daily_production = None

        self.monthly_production = None

        self.yearly_production = None

        self.energy_balance = None

        self.statistics = None