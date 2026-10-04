import pandas as pd

from helios.core.diagnostics.models import DiagnosticResult


class EnergyDiagnostics:
    """
    Diagnósticos sobre el balance energético FV.

    Este módulo no recalcula el balance. Trabaja exclusivamente
    sobre el DataFrame producido por SolarBalanceEngine.
    """

    HIGH_EXPORT_THRESHOLD = 0.50
    HIGH_GRID_DEPENDENCE_THRESHOLD = 0.50
    HOURLY_MISMATCH_THRESHOLD = 0.50

    REQUIRED_COLUMNS = {
        "consumption_kwh",
        "production_kwh",
        "self_consumption_kwh",
        "grid_import_kwh",
        "grid_export_kwh",
    }

    @classmethod
    def diagnose(
        cls,
        balance: pd.DataFrame,
    ) -> list[DiagnosticResult]:
        """
        Genera diagnósticos sobre el balance energético solar.
        """
        cls._validate_balance(balance)

        if balance.empty:
            return []

        diagnostics: list[DiagnosticResult] = []

        total_consumption = float(balance["consumption_kwh"].sum())
        total_production = float(balance["production_kwh"].sum())
        total_grid_import = float(balance["grid_import_kwh"].sum())
        total_grid_export = float(balance["grid_export_kwh"].sum())

        # ------------------------------------------------------------------
        # Excedente solar anual
        # ------------------------------------------------------------------
        export_ratio = (
            total_grid_export / total_production
            if total_production > 0.0
            else 0.0
        )

        if export_ratio >= cls.HIGH_EXPORT_THRESHOLD:
            diagnostics.append(
                DiagnosticResult(
                    code="HIGH_SOLAR_SURPLUS",
                    category="energy",
                    severity="warning",
                    title="Alto excedente solar",
                    description=(
                        "Una proporción elevada de la producción fotovoltaica "
                        "se vierte a la red en lugar de ser utilizada "
                        "directamente por la demanda."
                    ),
                    evidence={
                        "production_kwh": total_production,
                        "grid_export_kwh": total_grid_export,
                        "export_ratio_percent": export_ratio * 100.0,
                    },
                )
            )

        # ------------------------------------------------------------------
        # Dependencia de la red
        # ------------------------------------------------------------------
        grid_dependence = (
            total_grid_import / total_consumption
            if total_consumption > 0.0
            else 0.0
        )

        if grid_dependence >= cls.HIGH_GRID_DEPENDENCE_THRESHOLD:
            diagnostics.append(
                DiagnosticResult(
                    code="HIGH_GRID_DEPENDENCE",
                    category="energy",
                    severity="warning",
                    title="Alta dependencia de la red",
                    description=(
                        "Una proporción elevada de la demanda eléctrica "
                        "continúa dependiendo de energía importada de la red."
                    ),
                    evidence={
                        "consumption_kwh": total_consumption,
                        "grid_import_kwh": total_grid_import,
                        "grid_import_ratio_percent": grid_dependence * 100.0,
                    },
                )
            )

        # ------------------------------------------------------------------
        # Desajuste horario producción-demanda
        # ------------------------------------------------------------------
        mismatch = cls._calculate_hourly_mismatch(balance)

        if (
            mismatch["deficit_ratio_percent"]
            >= cls.HOURLY_MISMATCH_THRESHOLD * 100.0
            and mismatch["excess_ratio_percent"]
            >= cls.HOURLY_MISMATCH_THRESHOLD * 100.0
        ):
            diagnostics.append(
                DiagnosticResult(
                    code="HIGH_HOURLY_MISMATCH",
                    category="energy",
                    severity="info",
                    title="Desajuste horario entre producción y demanda",
                    description=(
                        "Existe simultáneamente un volumen significativo de "
                        "energía fotovoltaica excedente y de demanda que debe "
                        "cubrirse fuera de los periodos de producción solar. "
                        "Esto indica un desacoplamiento temporal entre "
                        "generación y consumo."
                    ),
                    evidence=mismatch,
                )
            )

        return diagnostics

    @classmethod
    def _calculate_hourly_mismatch(
        cls,
        balance: pd.DataFrame,
    ) -> dict[str, float]:
        """
        Calcula el desajuste horario entre producción y consumo.

        El cálculo se realiza hora a hora, distinguiendo entre:
        - excedente: producción superior al consumo;
        - déficit: consumo superior a la producción.

        Returns
        -------
        dict[str, float]
            Métricas agregadas del desajuste horario:
            - excess_energy_kwh
            - deficit_energy_kwh
            - excess_ratio_percent
            - deficit_ratio_percent
            - production_consumption_overlap_ratio_percent
        """
        cls._validate_balance(balance)

        if balance.empty:
            return {
                "excess_energy_kwh": 0.0,
                "deficit_energy_kwh": 0.0,
                "excess_ratio_percent": 0.0,
                "deficit_ratio_percent": 0.0,
                "production_consumption_overlap_ratio_percent": 0.0,
            }

        consumption = balance["consumption_kwh"].astype(float)
        production = balance["production_kwh"].astype(float)

        excess = (production - consumption).clip(lower=0.0)
        deficit = (consumption - production).clip(lower=0.0)

        total_production = float(production.sum())
        total_consumption = float(consumption.sum())

        excess_energy = float(excess.sum())
        deficit_energy = float(deficit.sum())

        excess_ratio = (
            excess_energy / total_production * 100.0
            if total_production > 0.0
            else 0.0
        )

        deficit_ratio = (
            deficit_energy / total_consumption * 100.0
            if total_consumption > 0.0
            else 0.0
        )

        overlap_energy = float(
            pd.concat(
                [consumption, production],
                axis=1,
            ).min(axis=1).sum()
        )

        overlap_ratio = (
            overlap_energy / total_consumption * 100.0
            if total_consumption > 0.0
            else 0.0
        )

        return {
            "excess_energy_kwh": excess_energy,
            "deficit_energy_kwh": deficit_energy,
            "excess_ratio_percent": excess_ratio,
            "deficit_ratio_percent": deficit_ratio,
            "production_consumption_overlap_ratio_percent": overlap_ratio,
        }

    @classmethod
    def _validate_balance(
        cls,
        balance: pd.DataFrame,
    ) -> None:
        if not isinstance(balance, pd.DataFrame):
            raise TypeError(
                "balance must be a pandas DataFrame."
            )

        missing_columns = (
            cls.REQUIRED_COLUMNS
            - set(balance.columns)
        )

        if missing_columns:
            raise ValueError(
                "Balance is missing required columns: "
                + ", ".join(sorted(missing_columns))
            )

        if balance.empty:
            raise ValueError(
                "Balance cannot be empty."
            )

        numeric_columns = (
            cls.REQUIRED_COLUMNS
        )

        for column in numeric_columns:
            if not pd.api.types.is_numeric_dtype(
                balance[column]
            ):
                raise TypeError(
                    f"Balance column '{column}' "
                    "must be numeric."
                )

            if balance[column].isna().any():
                raise ValueError(
                    f"Balance column '{column}' "
                    "cannot contain NaN values."
                )