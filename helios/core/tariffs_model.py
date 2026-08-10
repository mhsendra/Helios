from dataclasses import dataclass


@dataclass
class TariffPrices:

    buy_p1: float = 0.25
    buy_p2: float = 0.18
    buy_p3: float = 0.12

    sell_price: float = 0.06