import pytest

from helios.solar.installation_candidate import (
    InstallationCandidate
)


class TestInstallationCandidate:

    # ==================================================
    # Valid construction
    # ==================================================

    def test_creates_valid_candidate(self):

        candidate = InstallationCandidate(
            panel_count=15,
            panel_power_wp=540,
            panel_area_m2=2.5764,
        )

        assert candidate.panel_count == 15
        assert candidate.panel_power_wp == 540
        assert candidate.panel_area_m2 == 2.5764

    def test_creates_candidate_with_integer_values(self):

        candidate = InstallationCandidate(
            panel_count=10,
            panel_power_wp=500,
            panel_area_m2=6.0,
        )

        assert candidate.panel_count == 10
        assert candidate.panel_power_wp == 500
        assert candidate.panel_area_m2 == 6.0

    # ==================================================
    # panel_count validation
    # ==================================================

    @pytest.mark.parametrize(
        "value",
        [
            0,
            -1,
            -10,
        ]
    )
    def test_rejects_invalid_panel_count(
        self,
        value
    ):

        with pytest.raises(
            ValueError,
            match="Panel count must be at least one."
        ):

            InstallationCandidate(
                panel_count=value,
                panel_power_wp=540,
                panel_area_m2=2.5764,
            )

    # ==================================================
    # panel_power_wp validation
    # ==================================================

    @pytest.mark.parametrize(
        "value",
        [
            0,
            -1,
            -0.01,
        ]
    )
    def test_rejects_invalid_panel_power(
        self,
        value
    ):

        with pytest.raises(
            ValueError,
            match="Panel power must be greater than zero."
        ):

            InstallationCandidate(
                panel_count=15,
                panel_power_wp=value,
                panel_area_m2=2.5764,
            )

    # ==================================================
    # panel_area_m2 validation
    # ==================================================

    @pytest.mark.parametrize(
        "value",
        [
            0,
            -1,
            -0.01,
        ]
    )
    def test_rejects_invalid_panel_area(
        self,
        value
    ):

        with pytest.raises(
            ValueError,
            match="Panel area must be greater than zero."
        ):

            InstallationCandidate(
                panel_count=15,
                panel_power_wp=540,
                panel_area_m2=value,
            )

    # ==================================================
    # installed_power_kwp
    # ==================================================

    def test_calculates_installed_power(self):

        candidate = InstallationCandidate(
            panel_count=15,
            panel_power_wp=540,
            panel_area_m2=2.5764,
        )

        assert candidate.installed_power_kwp == pytest.approx(
            8.1
        )

    def test_calculates_installed_power_for_single_panel(self):

        candidate = InstallationCandidate(
            panel_count=1,
            panel_power_wp=540,
            panel_area_m2=2.5764,
        )

        assert candidate.installed_power_kwp == pytest.approx(
            0.54
        )

    def test_calculates_installed_power_for_multiple_panels(self):

        candidate = InstallationCandidate(
            panel_count=20,
            panel_power_wp=500,
            panel_area_m2=2.0,
        )

        assert candidate.installed_power_kwp == pytest.approx(
            10.0
        )

    def test_installed_power_uses_wp_to_kw_conversion(self):

        candidate = InstallationCandidate(
            panel_count=10,
            panel_power_wp=550,
            panel_area_m2=2.0,
        )

        assert candidate.installed_power_kwp == pytest.approx(
            5.5
        )

    # ==================================================
    # occupied_area_m2
    # ==================================================

    def test_calculates_occupied_area(self):

        candidate = InstallationCandidate(
            panel_count=15,
            panel_power_wp=540,
            panel_area_m2=2.5764,
        )

        assert candidate.occupied_area_m2 == pytest.approx(
            38.646
        )

    def test_calculates_occupied_area_for_single_panel(self):

        candidate = InstallationCandidate(
            panel_count=1,
            panel_power_wp=540,
            panel_area_m2=2.5764,
        )

        assert candidate.occupied_area_m2 == pytest.approx(
            2.5764
        )

    def test_calculates_occupied_area_for_multiple_panels(self):

        candidate = InstallationCandidate(
            panel_count=20,
            panel_power_wp=500,
            panel_area_m2=2.0,
        )

        assert candidate.occupied_area_m2 == pytest.approx(
            40.0
        )

    # ==================================================
    # Consistency between properties
    # ==================================================

    def test_power_scales_linearly_with_panel_count(self):

        one = InstallationCandidate(
            panel_count=1,
            panel_power_wp=540,
            panel_area_m2=2.5764,
        )

        ten = InstallationCandidate(
            panel_count=10,
            panel_power_wp=540,
            panel_area_m2=2.5764,
        )

        assert ten.installed_power_kwp == pytest.approx(
            one.installed_power_kwp * 10
        )

    def test_area_scales_linearly_with_panel_count(self):

        one = InstallationCandidate(
            panel_count=1,
            panel_power_wp=540,
            panel_area_m2=2.5764,
        )

        ten = InstallationCandidate(
            panel_count=10,
            panel_power_wp=540,
            panel_area_m2=2.5764,
        )

        assert ten.occupied_area_m2 == pytest.approx(
            one.occupied_area_m2 * 10
        )

    def test_power_and_area_are_independent(self):

        candidate = InstallationCandidate(
            panel_count=10,
            panel_power_wp=600,
            panel_area_m2=2.0,
        )

        assert candidate.installed_power_kwp == pytest.approx(
            6.0
        )

        assert candidate.occupied_area_m2 == pytest.approx(
            20.0
        )

    # ==================================================
    # Immutability
    # ==================================================

    def test_candidate_is_immutable(self):

        candidate = InstallationCandidate(
            panel_count=15,
            panel_power_wp=540,
            panel_area_m2=2.5764,
        )

        with pytest.raises(
            AttributeError
        ):

            candidate.panel_count = 20

    def test_candidate_power_is_immutable(self):

        candidate = InstallationCandidate(
            panel_count=15,
            panel_power_wp=540,
            panel_area_m2=2.5764,
        )

        with pytest.raises(
            AttributeError
        ):

            candidate.panel_power_wp = 600

    def test_candidate_area_is_immutable(self):

        candidate = InstallationCandidate(
            panel_count=15,
            panel_power_wp=540,
            panel_area_m2=2.5764,
        )

        with pytest.raises(
            AttributeError
        ):

            candidate.panel_area_m2 = 3.0

    @pytest.mark.parametrize(
    "value",
    [
        None,
        "15",
        15.5,
        True,
        False,
        object(),
    ],
)
    def test_rejects_invalid_panel_count_type(
        self,
        value,
    ):

        with pytest.raises(
            TypeError,
            match="Panel count must be an integer.",
        ):

            InstallationCandidate(
                panel_count=value,
                panel_power_wp=540,
                panel_area_m2=2.5764,
            )

    @pytest.mark.parametrize(
        "value",
        [
            None,
            "540",
            object(),
            True,
            False,
        ],
    )
    
    def test_rejects_invalid_panel_power_type(
        self,
        value,
    ):

        with pytest.raises(
            TypeError,
            match="Panel power must be a number.",
        ):

            InstallationCandidate(
                panel_count=15,
                panel_power_wp=value,
                panel_area_m2=2.5764,
            )

    @pytest.mark.parametrize(
        "value",
        [
            None,
            "2.5764",
            object(),
            True,
            False,
        ],
    )
    def test_rejects_invalid_panel_area_type(
        self,
        value,
    ):

        with pytest.raises(
            TypeError,
            match="Panel area must be a number.",
        ):

            InstallationCandidate(
                panel_count=15,
                panel_power_wp=540,
                panel_area_m2=value,
            )

    def test_accepts_minimum_panel_count(self):

        candidate = InstallationCandidate(
            panel_count=1,
            panel_power_wp=540,
            panel_area_m2=2.5764,
        )

        assert candidate.panel_count == 1

    def test_accepts_decimal_panel_power_and_area(self):

        candidate = InstallationCandidate(
            panel_count=15,
            panel_power_wp=540.5,
            panel_area_m2=2.5764,
        )

        assert candidate.panel_power_wp == pytest.approx(
            540.5
        )

        assert candidate.panel_area_m2 == pytest.approx(
            2.5764
        )

    # ==================================================
    # Dataclass behaviour
    # ==================================================

    def test_equal_candidates_are_equal(self):
    
        candidate_1 = InstallationCandidate(
            panel_count=15,
            panel_power_wp=540,
            panel_area_m2=2.5764,
        )

        candidate_2 = InstallationCandidate(
            panel_count=15,
            panel_power_wp=540,
            panel_area_m2=2.5764,
        )

        assert candidate_1 == candidate_2


    def test_different_candidates_are_not_equal(self):
    
        candidate_1 = InstallationCandidate(
            panel_count=15,
            panel_power_wp=540,
            panel_area_m2=2.5764,
        )

        candidate_2 = InstallationCandidate(
            panel_count=16,
            panel_power_wp=540,
            panel_area_m2=2.5764,
        )

        assert candidate_1 != candidate_2


    def test_candidate_has_dataclass_repr(self):
    
        candidate = InstallationCandidate(
            panel_count=15,
            panel_power_wp=540,
            panel_area_m2=2.5764,
        )

        representation = repr(candidate)

        assert "InstallationCandidate" in representation
        assert "panel_count=15" in representation
        assert "panel_power_wp=540" in representation
        assert "panel_area_m2=2.5764" in representation