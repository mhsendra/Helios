from helios.ev import (
    EVConfiguration,
    EVScenario,
    EVScenarioBuilder,
)


def test_ev_public_api_exports_configuration():

    assert EVConfiguration.__name__ == "EVConfiguration"


def test_ev_public_api_exports_scenario():

    assert EVScenario.__name__ == "EVScenario"


def test_ev_public_api_exports_builder():

    assert EVScenarioBuilder.__name__ == "EVScenarioBuilder"


def test_ev_public_api_defines_expected_exports():

    import helios.ev

    assert helios.ev.__all__ == [
        "EVConfiguration",
        "EVScenario",
        "EVScenarioBuilder",
    ]