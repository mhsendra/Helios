from dataclasses import dataclass

@dataclass
class SolarConfiguration:

    latitude: float

    longitude: float

    tilt: int

    azimuth: int

    reference_year: int = 2023

    losses: float = 14

    pv_technology: str = "crystSi"

    mounting_place: str = "building"