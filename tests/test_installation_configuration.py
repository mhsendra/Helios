import pytest

from helios.solar.installation_configuration import (
    InstallationConfiguration,
)

from helios.solar.installation_constraints import (
    InstallationConstraints,
)


class TestInstallationConfiguration:

    # ==================================================
    # Helpers
    # ==================================================

    def _configuration(self, **overrides):

        values = {
            "available_area_m2": 42.0,
            "panel_width_m": 1.134,
            "panel_height_m": 2.273,
            "panel_power_wp": 540,
        }

        values.update(overrides)

        return InstallationConfiguration(**values)

    # ==================================================
    # Construction
    # ==================================================

    def test_creates_configuration(self):

        configuration = self._configuration()

        assert isinstance(
            configuration,
            InstallationConfiguration,
        )

    def test_configuration_is_immutable(self):

        configuration = self._configuration()

        with pytest.raises(AttributeError):

            configuration.available_area_m2 = 50.0

    # ==================================================
    # Stored values
    # ==================================================

    def test_stores_basic_values(self):

        configuration = self._configuration(
            available_area_m2=50.0,
            panel_width_m=1.2,
            panel_height_m=2.0,
            panel_power_wp=550,
            min_panels=3,
            max_panels=15,
        )

        assert configuration.available_area_m2 == 50.0
        assert configuration.panel_width_m == 1.2
        assert configuration.panel_height_m == 2.0
        assert configuration.panel_power_wp == 550
        assert configuration.min_panels == 3
        assert configuration.max_panels == 15

    def test_default_values(self):

        configuration = self._configuration()

        assert configuration.min_panels == 1
        assert configuration.max_panels is None

        assert (
            configuration.maintenance_passage_required
            is False
        )

        assert (
            configuration.maintenance_passage_width_m
            == pytest.approx(0.45)
        )

        assert (
            configuration.maintenance_passage_orientation
            == "auto"
        )

        assert configuration.roof_width_m is None
        assert configuration.roof_height_m is None

    def test_stores_maintenance_passage_configuration(
        self,
    ):

        configuration = self._configuration(
            maintenance_passage_required=True,
            maintenance_passage_width_m=0.50,
            maintenance_passage_orientation="vertical",
            roof_width_m=6.50,
            roof_height_m=6.50,
        )

        assert (
            configuration.maintenance_passage_required
            is True
        )

        assert (
            configuration.maintenance_passage_width_m
            == pytest.approx(0.50)
        )

        assert (
            configuration.maintenance_passage_orientation
            == "vertical"
        )

        assert (
            configuration.roof_width_m
            == pytest.approx(6.50)
        )

        assert (
            configuration.roof_height_m
            == pytest.approx(6.50)
        )

    # ==================================================
    # Conversion
    # ==================================================

    def test_to_constraints_returns_installation_constraints(
        self,
    ):

        configuration = self._configuration()

        constraints = configuration.to_constraints()

        assert isinstance(
            constraints,
            InstallationConstraints,
        )

    def test_to_constraints_preserves_basic_values(
        self,
    ):

        configuration = self._configuration(
            available_area_m2=48.5,
            panel_width_m=1.10,
            panel_height_m=2.20,
            panel_power_wp=450,
            min_panels=2,
            max_panels=18,
        )

        constraints = configuration.to_constraints()

        assert (
            constraints.available_area_m2
            == pytest.approx(48.5)
        )

        assert (
            constraints.panel_width_m
            == pytest.approx(1.10)
        )

        assert (
            constraints.panel_height_m
            == pytest.approx(2.20)
        )

        assert (
            constraints.panel_power_wp
            == pytest.approx(450)
        )

        assert constraints.min_panels == 2
        assert constraints.max_panels == 18

    def test_to_constraints_preserves_maintenance_configuration(
        self,
    ):

        configuration = self._configuration(
            maintenance_passage_required=True,
            maintenance_passage_width_m=0.45,
            maintenance_passage_orientation="horizontal",
            roof_width_m=6.50,
            roof_height_m=7.20,
        )

        constraints = configuration.to_constraints()

        assert (
            constraints.maintenance_passage_required
            is True
        )

        assert (
            constraints.maintenance_passage_width_m
            == pytest.approx(0.45)
        )

        assert (
            constraints.maintenance_passage_orientation
            == "horizontal"
        )

        assert (
            constraints.roof_width_m
            == pytest.approx(6.50)
        )

        assert (
            constraints.roof_height_m
            == pytest.approx(7.20)
        )

    def test_to_constraints_preserves_none_max_panels(
        self,
    ):

        configuration = self._configuration(
            max_panels=None
        )

        constraints = configuration.to_constraints()

        assert constraints.max_panels is None

    def test_to_constraints_preserves_all_configuration_values(
        self,
    ):

        configuration = self._configuration(
            available_area_m2=42.25,
            panel_width_m=1.134,
            panel_height_m=2.273,
            panel_power_wp=540,
            min_panels=3,
            max_panels=20,
            maintenance_passage_required=True,
            maintenance_passage_width_m=0.45,
            maintenance_passage_orientation="vertical",
            roof_width_m=6.50,
            roof_height_m=6.50,
        )

        constraints = configuration.to_constraints()

        assert (
            constraints.available_area_m2
            == pytest.approx(
                configuration.available_area_m2
            )
        )

        assert (
            constraints.panel_width_m
            == pytest.approx(
                configuration.panel_width_m
            )
        )

        assert (
            constraints.panel_height_m
            == pytest.approx(
                configuration.panel_height_m
            )
        )

        assert (
            constraints.panel_power_wp
            == pytest.approx(
                configuration.panel_power_wp
            )
        )

        assert (
            constraints.min_panels
            == configuration.min_panels
        )

        assert (
            constraints.max_panels
            == configuration.max_panels
        )

        assert (
            constraints.maintenance_passage_required
            == configuration.maintenance_passage_required
        )

        assert (
            constraints.maintenance_passage_width_m
            == pytest.approx(
                configuration.maintenance_passage_width_m
            )
        )

        assert (
            constraints.maintenance_passage_orientation
            == configuration.maintenance_passage_orientation
        )

        assert (
            constraints.roof_width_m
            == pytest.approx(
                configuration.roof_width_m
            )
        )

        assert (
            constraints.roof_height_m
            == pytest.approx(
                configuration.roof_height_m
            )
        )

    # ==================================================
    # Constraint validation delegation
    # ==================================================

    def test_to_constraints_preserves_invalid_configuration_behavior(
        self,
    ):

        configuration = self._configuration(
            available_area_m2=-1.0
        )

        with pytest.raises(
            ValueError,
            match="Available area must be greater than zero.",
        ):

            configuration.to_constraints()

    def test_to_constraints_rejects_invalid_panel_dimensions(
        self,
    ):

        configuration = self._configuration(
            panel_width_m=0.0
        )

        with pytest.raises(
            ValueError,
            match="Panel width must be greater than zero.",
        ):

            configuration.to_constraints()

    def test_to_constraints_rejects_invalid_panel_power(
        self,
    ):

        configuration = self._configuration(
            panel_power_wp=0.0
        )

        with pytest.raises(
            ValueError,
            match="Panel power must be greater than zero.",
        ):

            configuration.to_constraints()

    def test_to_constraints_rejects_invalid_panel_limits(
        self,
    ):

        configuration = self._configuration(
            min_panels=10,
            max_panels=5,
        )

        with pytest.raises(
            ValueError,
            match=(
                "Maximum number of panels cannot be "
                "less than minimum number of panels."
            ),
        ):

            configuration.to_constraints()

    def test_to_constraints_rejects_invalid_maintenance_configuration(
        self,
    ):

        configuration = self._configuration(
            maintenance_passage_required=True,
            roof_width_m=None,
            roof_height_m=6.50,
        )

        with pytest.raises(
            ValueError,
            match=(
                "Roof width is required when a "
                "maintenance passage is enabled."
            ),
        ):

            configuration.to_constraints()

    # ==================================================
    # Determinism
    # ==================================================

    def test_to_constraints_is_deterministic(self):

        configuration = self._configuration(
            maintenance_passage_required=True,
            roof_width_m=6.50,
            roof_height_m=6.50,
        )

        first = configuration.to_constraints()
        second = configuration.to_constraints()

        assert first == second

    def test_to_constraints_creates_independent_objects(self):

        configuration = self._configuration()

        first = configuration.to_constraints()
        second = configuration.to_constraints()

        assert first is not second
        assert first == second