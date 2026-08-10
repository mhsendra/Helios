import pandas as pd

class ReportPrinter:

    TOTAL_WIDTH = 55
    LABEL_WIDTH = 28
    VALUE_WIDTH = 12

    @classmethod
    def _print_line(
        cls,
        label: str,
        value: str
    ):

        dots = "." * (
            cls.TOTAL_WIDTH
            - len(label)
            - len(value)
            - 1
        )

        print(
            f"{label}{dots} {value}"
        )

    @classmethod
    def text(
        cls,
        label,
        value
    ):

        cls._print_line(
            label,
            str(value)
        )

    @classmethod
    def hours(
        cls,
        label: str,
        value: int
    ):

        cls._print_line(
            label,
            f"{int(value)}"
        )

    @classmethod
    def percent(
        cls,
        label: str,
        value: float,
        decimals: int = 2
    ):

        cls._print_line(
            label,
            f"{value:.{decimals}f} %"
        )

    @classmethod
    def energy(
        cls,
        label: str,
        value: float,
        decimals: int = 2
    ):

        cls._print_line(
            label,
            f"{value:.{decimals}f} kWh"
        )

    @classmethod
    def datetime(
        cls,
        label: str,
        value
    ):

        if value is None:

            text = "-"

        else:

            text = value.strftime("%d/%m/%Y %H:%M")

        cls._print_line(
            label,
            text
        )

    @classmethod
    def day(
        cls,
        label: str,
        value
    ):

        if pd.isna(value):
            text = "---"
        else:
            text = pd.Timestamp(value).strftime("%d/%m/%Y")

        cls._print_line(
            label,
            text
        )

    @classmethod
    def month(
        cls,
        label: str,
        value
    ):

        if pd.isna(value):

            text = "---"

        else:

            meses = [
                "Enero", "Febrero", "Marzo", "Abril",
                "Mayo", "Junio", "Julio", "Agosto",
                "Septiembre", "Octubre", "Noviembre", "Diciembre"
            ]

            ts = pd.Timestamp(value)

            text = f"{meses[ts.month - 1]} {ts.year}"

        cls._print_line(
            label,
            text
        )

    @classmethod
    def year(
        cls,
        label: str,
        value
    ):

        if pd.isna(value):
            text = "---"
        else:
            text = str(pd.Timestamp(value).year)

        cls._print_line(
            label,
            text
        )

    @classmethod
    def count(
        cls,
        label: str,
        value: int
    ):

        cls._print_line(
            label,
            f"{int(value)}"
        )

    @classmethod
    def quality(
        cls,
        label: str,
        value: str
    ):

        cls._print_line(
            label,
            value.upper()
        )
        
    @classmethod
    def title(cls, text):

        print()
        print("=" * 55)
        print(f"HELIOS - {text}")
        print("=" * 55)

    @classmethod
    def table_header(
        cls,
        columns: list[str],
        widths: list[int],
        align: list[str] | None = None
    ):

        if align is None:
            align = ["left"] * len(columns)

        row = ""

        for text, width, mode in zip(columns, widths, align):

            if mode == "right":
                row += f"{text:>{width}}"
            else:
                row += f"{text:<{width}}"

        print(row)
        print("-" * sum(widths))

    @classmethod
    def table_row(
        cls,
        values: list[str],
        widths: list[int],
        align: list[str] | None = None
    ):

        if align is None:
            align = ["left"] * len(values)

        row = ""

        for value, width, mode in zip(values, widths, align):

            if mode == "right":
                row += f"{value:>{width}}"
            else:
                row += f"{value:<{width}}"

        print(row)

    @classmethod
    def blank(cls):

        print()

    @classmethod
    def line(cls, label, value="", unit=""):

        print(
            f"{label:.<{cls.LABEL_WIDTH}} "
            f"{str(value):>{cls.VALUE_WIDTH}} {unit}"
        )

    @classmethod
    def subtitle(cls, text):

        print()
        print(text)
        print("-" * cls.TOTAL_WIDTH)

    @classmethod
    def value(
        cls,
        label: str,
        value,
        unit: str = "",
        decimals: int | None = None
    ):

        if isinstance(value, float) and decimals is not None:
            text = f"{value:.{decimals}f}"
        else:
            text = str(value)

        if unit:
            text += f" {unit}"

        cls._print_line(label, text)