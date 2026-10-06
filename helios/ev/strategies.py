import pandas as pd

from helios.core.consumption_scenario import ConsumptionScenario
from helios.ev.charging_strategy import EVChargingStrategy
from helios.ev.scenario import EVScenario
from helios.solar.production_profile import SolarProductionProfile
from helios.ev.solar_charging_strategy import SolarChargingStrategy

def _distribute_daily_energy_in_window(
        profile: pd.Series,
        daily_energy: pd.Series,
        start_hour: int,
        end_hour: int,
    ) -> pd.Series:
        """Distribuye energía diaria uniformemente dentro de una ventana horaria.

        Parameters
        ----------
        profile:
            Serie horaria cuyo índice define las horas disponibles.
        daily_energy:
            Energía a distribuir para cada día, indexada por fecha normalizada.
        start_hour:
            Hora inicial de la ventana, inclusiva.
        end_hour:
            Hora final de la ventana, exclusiva.

        Returns
        -------
        pd.Series
            Serie horaria con la energía distribuida.
        """
        result = pd.Series(
            0.0,
            index=profile.index,
            dtype=float,
        )

        for day, energy in daily_energy.items():
            day = pd.Timestamp(day).normalize()
            energy = float(energy)

            charging_hours = result.loc[
                (
                    result.index.normalize() == day
                )
                & (
                    result.index.hour >= start_hour
                )
                & (
                    result.index.hour < end_hour
                )
            ].index

            if len(charging_hours) == 0:
                raise ValueError(
                    "Charging window does not contain "
                    "any hours for the scenario."
                )

            energy_per_hour = energy / len(charging_hours)

            result.loc[charging_hours] = energy_per_hour

        return result

class ImmediateChargingStrategy(EVChargingStrategy):
    """Mantiene la demanda EV en las mismas horas del escenario de entrada."""

    def apply(self, scenario: EVScenario) -> EVScenario:
        if not isinstance(scenario, EVScenario):
            raise TypeError(
                "scenario must be an EVScenario."
            )

        return EVScenario(
            hourly_consumption=scenario.hourly_consumption.copy(),
            reference_year=scenario.reference_year,
        )

class NightChargingStrategy(EVChargingStrategy):
    """Concentra la demanda EV diaria en una ventana nocturna."""

    def __init__(
        self,
        start_hour: int = 0,
        end_hour: int = 7,
    ) -> None:
        if not 0 <= start_hour <= 23:
            raise ValueError(
                "start_hour must be between 0 and 23."
            )

        if not 1 <= end_hour <= 24:
            raise ValueError(
                "end_hour must be between 1 and 24."
            )

        if start_hour >= end_hour:
            raise ValueError(
                "start_hour must be lower than end_hour."
            )

        self.start_hour = start_hour
        self.end_hour = end_hour

    def apply(self, scenario: EVScenario) -> EVScenario:
        if not isinstance(scenario, EVScenario):
            raise TypeError(
                "scenario must be an EVScenario."
            )

        daily_energy = (
            scenario.hourly_consumption
            .groupby(
                scenario.hourly_consumption.index.normalize()
            )
            .sum()
        )

        result = _distribute_daily_energy_in_window(
            profile=scenario.hourly_consumption,
            daily_energy=daily_energy,
            start_hour=self.start_hour,
            end_hour=self.end_hour,
        )

        return EVScenario(
            hourly_consumption=result,
            reference_year=scenario.reference_year,
        )


class SolarSurplusChargingStrategy(SolarChargingStrategy):
    """Carga el EV utilizando primero el excedente fotovoltaico horario."""

    def apply(
        self,
        ev_scenario: EVScenario,
        consumption_scenario: ConsumptionScenario,
        production_profile: SolarProductionProfile,
    ) -> EVScenario:
        if not isinstance(ev_scenario, EVScenario):
            raise TypeError(
                "ev_scenario must be an EVScenario."
            )

        if not isinstance(
            consumption_scenario,
            ConsumptionScenario,
        ):
            raise TypeError(
                "consumption_scenario must be a ConsumptionScenario."
            )

        if not isinstance(
            production_profile,
            SolarProductionProfile,
        ):
            raise TypeError(
                "production_profile must be a SolarProductionProfile."
            )

        if ev_scenario.reference_year != consumption_scenario.reference_year:
            raise ValueError(
                "EV scenario and consumption scenario must use "
                "the same reference year."
            )

        if ev_scenario.reference_year != production_profile.reference_year:
            raise ValueError(
                "EV scenario and production profile must use "
                "the same reference year."
            )

        domestic_consumption = (
            consumption_scenario.hourly_consumption
        )

        production = production_profile.hourly_production

        production_lookup = production.copy()
        production_lookup.index = (
            production_lookup.index.strftime("%m-%d-%H")
        )

        profile_key = domestic_consumption.index.strftime(
            "%m-%d-%H"
        )

        aligned_production = (
            pd.Series(
                profile_key,
                index=domestic_consumption.index,
            )
            .map(production_lookup)
            .fillna(0.0)
        )

        surplus = (
            aligned_production
            - domestic_consumption
        ).clip(lower=0.0)

        original_ev = ev_scenario.hourly_consumption.copy()

        solar_charge = pd.Series(
            0.0,
            index=original_ev.index,
            dtype=float,
        )

        remaining_energy = float(
            ev_scenario.annual_consumption
        )

        # Primera prioridad:
        # utilizar exclusivamente el excedente FV.
        for timestamp in surplus.index:
            if remaining_energy <= 0.0:
                break

            available_surplus = float(
                surplus.loc[timestamp]
            )

            if available_surplus <= 0.0:
                continue

            charge = min(
                available_surplus,
                remaining_energy,
            )

            solar_charge.loc[timestamp] = charge
            remaining_energy -= charge

        # Segunda prioridad:
        # repartir la energía restante únicamente entre las
        # horas que todavía no han recibido carga solar.
        if remaining_energy > 0.0:
            fallback_profile = original_ev.where(
                solar_charge == 0.0,
                0.0,
            )

            fallback_energy = float(
                fallback_profile.sum()
            )

            if fallback_energy <= 0.0:
                raise ValueError(
                    "Cannot allocate remaining EV energy "
                    "without exceeding solar charging hours."
                )

            fallback_profile = (
                fallback_profile
                * remaining_energy
                / fallback_energy
            )

            solar_charge += fallback_profile

        return EVScenario(
            hourly_consumption=solar_charge,
            reference_year=ev_scenario.reference_year,
        )

class SolarNightChargingStrategy(SolarChargingStrategy):
    """Prioriza el excedente FV y usa la noche como fallback."""

    def __init__(
        self,
        start_hour: int = 0,
        end_hour: int = 7,
    ) -> None:
        if not 0 <= start_hour <= 23:
            raise ValueError(
                "start_hour must be between 0 and 23."
            )

        if not 1 <= end_hour <= 24:
            raise ValueError(
                "end_hour must be between 1 and 24."
            )

        if start_hour >= end_hour:
            raise ValueError(
                "start_hour must be lower than end_hour."
            )

        self.start_hour = start_hour
        self.end_hour = end_hour

    def apply(
        self,
        ev_scenario: EVScenario,
        consumption_scenario: ConsumptionScenario,
        production_profile: SolarProductionProfile,
    ) -> EVScenario:
        if not isinstance(ev_scenario, EVScenario):
            raise TypeError(
                "ev_scenario must be an EVScenario."
            )

        if not isinstance(
            consumption_scenario,
            ConsumptionScenario,
        ):
            raise TypeError(
                "consumption_scenario must be a ConsumptionScenario."
            )

        if not isinstance(
            production_profile,
            SolarProductionProfile,
        ):
            raise TypeError(
                "production_profile must be a SolarProductionProfile."
            )

        if (
            ev_scenario.reference_year
            != consumption_scenario.reference_year
        ):
            raise ValueError(
                "EV scenario and consumption scenario must use "
                "the same reference year."
            )

        if (
            ev_scenario.reference_year
            != production_profile.reference_year
        ):
            raise ValueError(
                "EV scenario and production profile must use "
                "the same reference year."
            )

        domestic_consumption = (
            consumption_scenario.hourly_consumption
        )

        production = production_profile.hourly_production

        production_lookup = production.copy()
        production_lookup.index = (
            production_lookup.index.strftime("%m-%d-%H")
        )

        profile_key = domestic_consumption.index.strftime(
            "%m-%d-%H"
        )

        aligned_production = (
            pd.Series(
                profile_key,
                index=domestic_consumption.index,
            )
            .map(production_lookup)
            .fillna(0.0)
        )

        surplus = (
            aligned_production
            - domestic_consumption
        ).clip(lower=0.0)

        original_ev = ev_scenario.hourly_consumption.copy()

        result = pd.Series(
            0.0,
            index=original_ev.index,
            dtype=float,
        )

        for day, daily_values in original_ev.groupby(
            original_ev.index.normalize()
        ):
            daily_ev_energy = float(daily_values.sum())

            if daily_ev_energy <= 0.0:
                continue

            day_mask = (
                original_ev.index.normalize() == day
            )

            day_surplus = surplus.loc[day_mask]

            remaining_energy = daily_ev_energy

            for timestamp in day_surplus.index:
                available_surplus = float(
                    day_surplus.loc[timestamp]
                )

                if available_surplus <= 0.0:
                    continue

                charge = min(
                    available_surplus,
                    remaining_energy,
                )

                result.loc[timestamp] += charge
                remaining_energy -= charge

                if remaining_energy <= 0.0:
                    break

            if remaining_energy > 0.0:
                remaining_profile = original_ev.loc[
                    day_mask
                ]

                night_energy = (
                    remaining_profile
                    * 0.0
                )

                night_mask = (
                    night_energy.index.hour >= self.start_hour
                ) & (
                    night_energy.index.hour < self.end_hour
                )

                night_profile = (
                    remaining_profile.where(
                        night_mask,
                        0.0,
                    )
                )

                daily_night_energy = float(
                    night_profile.sum()
                )

                if daily_night_energy > 0.0:
                    fallback = (
                        night_profile
                        * remaining_energy
                        / daily_night_energy
                    )
                else:
                    fallback = (
                        _distribute_daily_energy_in_window(
                            profile=original_ev.loc[day_mask],
                            daily_energy=pd.Series(
                                [remaining_energy],
                                index=[day],
                            ),
                            start_hour=self.start_hour,
                            end_hour=self.end_hour,
                        )
                    )

                result.loc[fallback.index] += fallback

        return EVScenario(
            hourly_consumption=result,
            reference_year=ev_scenario.reference_year,
        )