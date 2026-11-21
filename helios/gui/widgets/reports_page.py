from io import StringIO
import os
from pathlib import Path
from datetime import datetime
from contextlib import redirect_stdout

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QGridLayout,
    QGroupBox,
    QTextEdit,
    QFileDialog,
    QMessageBox,
    QScrollArea,
)

from helios.reports.solar_report_data_factory import (
    SolarReportDataFactory,
)

from helios.reports.solar_report_generator import (
    SolarReportGenerator,
)

from helios.utils.platform import is_android

class ReportsPage(QWidget):

    def __init__(self, project):

        super().__init__()

        self.project = project

        if is_android():
            outer_layout = QVBoxLayout(self)

            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)

            content = QWidget()
            layout = QVBoxLayout(content)

            scroll_area.setWidget(content)
            outer_layout.addWidget(scroll_area)

            self.scroll_area = scroll_area

        else:
            layout = QVBoxLayout(self)

        # ==================================================
        # Título
        # ==================================================

        title = QLabel("<h2>Informes</h2>")

        layout.addWidget(title)

        # ==================================================
        # Perfiles
        # ==================================================

        profiles_group = QGroupBox(
            "Perfiles de consumo"
        )

        profiles_layout = QGridLayout()

        self.hourly_button = QPushButton(
            "Perfil horario"
        )

        self.weekday_button = QPushButton(
            "Perfil semanal"
        )

        self.monthly_button = QPushButton(
            "Perfil mensual"
        )

        self.seasonal_button = QPushButton(
            "Perfil estacional"
        )

        profiles_layout.addWidget(
            self.hourly_button,
            0,
            0
        )

        profiles_layout.addWidget(
            self.weekday_button,
            0,
            1
        )

        profiles_layout.addWidget(
            self.monthly_button,
            1,
            0
        )

        profiles_layout.addWidget(
            self.seasonal_button,
            1,
            1
        )

        profiles_group.setLayout(
            profiles_layout
        )

        # ==================================================
        # Indicadores
        # ==================================================

        indicators_group = QGroupBox(
            "Indicadores"
        )

        indicators_layout = QGridLayout()

        self.mean_consumption_button = QPushButton(
            "Consumo medio"
        )

        self.extremes_button = QPushButton(
            "Extremos de consumo"
        )

        self.base_load_button = QPushButton(
            "Carga base"
        )

        indicators_layout.addWidget(
            self.mean_consumption_button,
            0,
            0
        )

        indicators_layout.addWidget(
            self.extremes_button,
            0,
            1
        )

        indicators_layout.addWidget(
            self.base_load_button,
            1,
            0
        )

        indicators_group.setLayout(
            indicators_layout
        )

        # ==================================================
        # Comparativas
        # ==================================================

        comparisons_group = QGroupBox(
            "Comparativas"
        )

        comparisons_layout = QGridLayout()

        self.monthly_comparison_button = QPushButton(
            "Comparativa mensual"
        )

        self.monthly_variation_button = QPushButton(
            "Variación mensual"
        )

        self.weekly_comparison_button = QPushButton(
            "Comparativa semanal"
        )

        self.weekly_variation_button = QPushButton(
            "Variación semanal"
        )

        self.yearly_comparison_button = QPushButton(
            "Comparativa anual"
        )

        comparisons_layout.addWidget(
            self.monthly_comparison_button,
            0,
            0
        )

        comparisons_layout.addWidget(
            self.monthly_variation_button,
            0,
            1
        )

        comparisons_layout.addWidget(
            self.weekly_comparison_button,
            1,
            0
        )

        comparisons_layout.addWidget(
            self.weekly_variation_button,
            1,
            1
        )

        comparisons_layout.addWidget(
            self.yearly_comparison_button,
            2,
            0
        )

        comparisons_group.setLayout(
            comparisons_layout
        )

        # ==================================================
        # Estadísticas
        # ==================================================

        statistics_group = QGroupBox(
            "Estadísticas"
        )

        statistics_layout = QGridLayout()

        self.statistics_button = QPushButton(
            "Estadísticas generales"
        )

        self.daily_statistics_button = QPushButton(
            "Estadísticas diarias"
        )

        self.monthly_statistics_button = QPushButton(
            "Estadísticas mensuales"
        )

        self.yearly_statistics_button = QPushButton(
            "Estadísticas anuales"
        )

        statistics_layout.addWidget(
            self.statistics_button,
            0,
            0
        )

        statistics_layout.addWidget(
            self.daily_statistics_button,
            0,
            1
        )

        statistics_layout.addWidget(
            self.monthly_statistics_button,
            1,
            0
        )

        statistics_layout.addWidget(
            self.yearly_statistics_button,
            1,
            1
        )

        statistics_group.setLayout(
            statistics_layout
        )

        # ==================================================
        # Tarifas
        # ==================================================

        tariffs_group = QGroupBox(
            "Tarifas eléctricas"
        )

        tariffs_layout = QGridLayout()

        self.tariff_periods_button = QPushButton(
            "Periodos tarifarios"
        )

        tariffs_layout.addWidget(
            self.tariff_periods_button,
            0,
            0
        )

        tariffs_group.setLayout(
            tariffs_layout
        )

        # ==================================================
        # Economía
        # ==================================================

        economics_group = QGroupBox(
            "Economía"
        )

        economics_layout = QGridLayout()

        self.annual_economics_button = QPushButton(
            "Informe económico anual"
        )

        self.economic_scenarios_button = QPushButton(
            "Escenarios económicos"
        )

        economics_layout.addWidget(
            self.annual_economics_button,
            0,
            0
        )

        economics_layout.addWidget(
            self.economic_scenarios_button,
            0,
            1
        )

        economics_group.setLayout(
            economics_layout
        )

        # ==================================================
        # Informe solar PDF
        # ==================================================

        solar_report_group = QGroupBox(
            "Informe solar"
        )

        solar_report_layout = QVBoxLayout()

        self.generate_solar_pdf_button = QPushButton(
            "Generar informe solar PDF"
        )

        self.generate_solar_pdf_button.setEnabled(
            False
        )

        if not is_android():
            solar_report_layout.addWidget(
                self.generate_solar_pdf_button
            )

        solar_report_group.setLayout(
            solar_report_layout
        )

        # ==================================================
        # Distribución de grupos
        # ==================================================

        groups_layout = QGridLayout()

        groups = [
            profiles_group,
            indicators_group,
            comparisons_group,
            statistics_group,
            tariffs_group,
            economics_group,
            solar_report_group,
        ]

        if is_android():
            # Android: grupos en una sola columna.
            # El botón PDF está en el pie fijo, fuera del scroll.
            android_groups = [
                group for group in groups
                if group is not solar_report_group
            ]

            for row, group in enumerate(android_groups):
                groups_layout.addWidget(group, row, 0)

            groups_layout.setColumnStretch(0, 1)

        else:
            # Escritorio: conservar la distribución original.
            groups_layout.addWidget(profiles_group, 0, 0)
            groups_layout.addWidget(indicators_group, 0, 1)
            groups_layout.addWidget(comparisons_group, 1, 0)
            groups_layout.addWidget(statistics_group, 1, 1)
            groups_layout.addWidget(tariffs_group, 2, 0)
            groups_layout.addWidget(economics_group, 2, 1)
            groups_layout.addWidget(solar_report_group, 3, 0, 1, 2)

            groups_layout.setColumnStretch(0, 1)
            groups_layout.setColumnStretch(1, 1)

        layout.addLayout(
            groups_layout
        )
        # ==================================================
        # Área del informe
        # ==================================================

        layout.addWidget(
            QLabel("<h3>Informe</h3>")
        )

        self.report_output = QTextEdit()

        self.report_output.setReadOnly(True)

        layout.addWidget(
            self.report_output,
            1
        )

        if is_android():
            # Pie fijo, fuera del QScrollArea.
            outer_layout.addWidget(
                self.generate_solar_pdf_button
            )

        # ==================================================
        # Conexiones
        # ==================================================

        self.hourly_button.clicked.connect(
            self.show_hourly_report
        )

        self.weekday_button.clicked.connect(
            self.show_weekday_report
        )

        self.monthly_button.clicked.connect(
            self.show_monthly_report
        )

        self.seasonal_button.clicked.connect(
            self.show_seasonal_report
        )

        self.mean_consumption_button.clicked.connect(
            self.show_mean_consumption_report
        )

        self.extremes_button.clicked.connect(
            self.show_extremes_report
        )

        self.base_load_button.clicked.connect(
            self.show_base_load_report
        )

        self.monthly_comparison_button.clicked.connect(
            self.show_monthly_comparison_report
        )

        self.monthly_variation_button.clicked.connect(
            self.show_monthly_variation_report
        )

        self.weekly_comparison_button.clicked.connect(
            self.show_weekly_comparison_report
        )

        self.weekly_variation_button.clicked.connect(
            self.show_weekly_variation_report
        )

        self.yearly_comparison_button.clicked.connect(
            self.show_yearly_comparison_report
        )

        self.statistics_button.clicked.connect(
            self.show_statistics_report
        )

        self.daily_statistics_button.clicked.connect(
            self.show_daily_statistics_report
        )

        self.monthly_statistics_button.clicked.connect(
            self.show_monthly_statistics_report
        )

        self.yearly_statistics_button.clicked.connect(
            self.show_yearly_statistics_report
        )

        self.tariff_periods_button.clicked.connect(
            self.show_tariff_periods_report
        )

        self.annual_economics_button.clicked.connect(
            self.show_annual_economics_report
        )

        self.economic_scenarios_button.clicked.connect(
            self.show_economic_scenarios_report
        )

        self.generate_solar_pdf_button.clicked.connect(
            self.generate_solar_pdf_report
        )

    # ==================================================
    # Captura de informes
    # ==================================================

    def _show_report(self, report_function):

        buffer = StringIO()

        with redirect_stdout(buffer):
            report_function()

        report = buffer.getvalue()

        self.report_output.setPlainText(
            report
        )

    # ==================================================
    # Informes de perfiles
    # ==================================================

    def show_hourly_report(self):

        self._show_report(
            self.project.profiles.hourly_profile_report
        )

    def show_weekday_report(self):

        self._show_report(
            self.project.profiles.weekday_profile_report
        )

    def show_monthly_report(self):

        self._show_report(
            self.project.profiles.monthly_profile_report
        )

    def show_seasonal_report(self):

        self._show_report(
            self.project.profiles.seasonal_profile_report
        )

    # ==================================================
    # Informes de indicadores
    # ==================================================

    def show_mean_consumption_report(self):

        self._show_report(
            self.project.indicators.mean_consumption_report
        )

    def show_extremes_report(self):

        self._show_report(
            self.project.indicators.extremes_report
        )

    def show_base_load_report(self):

        self._show_report(
            self.project.indicators.base_load_report
        )

    # ==================================================
    # Informes de comparativas
    # ==================================================

    def show_monthly_comparison_report(self):

        self._show_report(
            self.project.comparisons.monthly_comparison_report
        )

    def show_monthly_variation_report(self):

        self._show_report(
            self.project.comparisons.monthly_variation_report
        )

    def show_weekly_comparison_report(self):

        self._show_report(
            self.project.comparisons.weekly_comparison_report
        )

    def show_weekly_variation_report(self):

        self._show_report(
            self.project.comparisons.weekly_variation_report
        )

    def show_yearly_comparison_report(self):

        self._show_report(
            self.project.comparisons.yearly_comparison_report
        )

    # ==================================================
    # Informes de estadísticas
    # ==================================================

    def show_statistics_report(self):

        self._show_report(
            self.project.statistics.statistics_report
        )

    def show_daily_statistics_report(self):

        self._show_report(
            self.project.statistics.daily_report
        )

    def show_monthly_statistics_report(self):

        self._show_report(
            self.project.statistics.monthly_report
        )

    def show_yearly_statistics_report(self):

        self._show_report(
            self.project.statistics.yearly_report
        )

    # ==================================================
    # Informes de tarifas
    # ==================================================

    def show_tariff_periods_report(self):

        self._show_report(
            self.project.tariffs.tariff_periods_report
        )

    # ==================================================
    # Informes de economía
    # ==================================================

    def show_annual_economics_report(self):

        self._show_report(
            self.project.economics.annual_economics_report
        )

    def show_economic_scenarios_report(self):

        self._show_report(
            self.project.economics.economic_scenarios_report
        )

    # ==================================================
    # Informe solar PDF
    # ==================================================

    def set_solar_report_available(
        self,
        available: bool,
    ):

        self.generate_solar_pdf_button.setEnabled(
            available
        )

    # HELIOS_PDF_DIAG_BEGIN
    @staticmethod
    def _pdf_diagnostic(message):
        if not is_android():
            return

        try:
            private = os.environ.get("ANDROID_PRIVATE")
            if not private:
                print(
                    "HELIOS_PDF_DIAG: ANDROID_PRIVATE missing",
                    flush=True,
                )
                return

            directory = Path(private) / "helios_pdf"
            directory.mkdir(parents=True, exist_ok=True)

            logfile = directory / "pdf_debug.log"

            timestamp = datetime.now().isoformat(
                timespec="milliseconds"
            )

            line = f"{timestamp} | {message}"

            with logfile.open("a", encoding="utf-8") as stream:
                stream.write(line + "\n")
                stream.flush()
                os.fsync(stream.fileno())

            print("HELIOS_PDF_DIAG:", line, flush=True)

        except Exception as error:
            print(
                "HELIOS_PDF_DIAG logging error:",
                repr(error),
                flush=True,
            )

    def generate_solar_pdf_report(self):
        if is_android():
            self._generate_android_solar_pdf_report()
            return

        self._pdf_diagnostic("01 BEFORE_FILE_DIALOG")

        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar informe solar",
            "Informe_solar.pdf",
            "PDF (*.pdf)",
        )

        self._pdf_diagnostic(
            f"02 AFTER_FILE_DIALOG path={output_path!r}"
        )

        if not output_path:
            self._pdf_diagnostic("03 FILE_DIALOG_CANCELLED")
            return

        self._generate_solar_pdf_to_path(output_path)

    def _generate_solar_pdf_to_path(self, output_path):
        try:
            self._pdf_diagnostic("04 BEFORE_DATA_FACTORY")

            data = SolarReportDataFactory.create(
                self.project.analyzer.solar,
                self.project.analyzer.economics,
            )

            self._pdf_diagnostic("05 AFTER_DATA_FACTORY")

            generator = SolarReportGenerator()

            self._pdf_diagnostic("06 BEFORE_GENERATE")

            generator.generate(data, str(output_path))

            self._pdf_diagnostic("07 AFTER_GENERATE")

        except Exception as error:
            self._pdf_diagnostic(
                f"08 EXCEPTION {type(error).__name__}: {error}"
            )

            QMessageBox.critical(
                self,
                "Error",
                (
                    "No se ha podido generar el informe solar.\\n\\n"
                    f"{error}"
                ),
            )
            return False

        return True

    def _generate_android_solar_pdf_report(self):
        import uuid
        from PySide6.QtCore import QTimer

        if getattr(self, "_pdf_request_id", None) is not None:
            return

        output_path = None

        try:
            private = os.environ.get("ANDROID_PRIVATE")
            if not private:
                raise RuntimeError("ANDROID_PRIVATE no está definido")

            directory = Path(private) / "helios_pdf"
            directory.mkdir(parents=True, exist_ok=True)

            request_id = str(uuid.uuid4())
            output_path = directory / f"{request_id}.pdf"

            request = directory / "pdf_request.txt"
            result = directory / "pdf_result.txt"

            result.unlink(missing_ok=True)

            self._pdf_diagnostic(
                f"11 ANDROID_GENERATE_BEGIN id={request_id}"
            )

            if not self._generate_solar_pdf_to_path(output_path):
                output_path.unlink(missing_ok=True)
                return

            if not output_path.is_file():
                raise FileNotFoundError(str(output_path))

            if output_path.stat().st_size == 0:
                raise ValueError("El informe PDF generado está vacío")

            self._pdf_diagnostic(
                f"12 ANDROID_PDF_READY bytes={output_path.stat().st_size}"
            )

            if getattr(self, "_pdf_timer", None) is None:
                self._pdf_timer = QTimer(self)
                self._pdf_timer.setInterval(300)
                self._pdf_timer.timeout.connect(
                    self._check_android_pdf_result
                )

            self._pdf_request_id = request_id
            self._pdf_directory = directory
            self._pdf_output_path = output_path

            self._pdf_button_was_enabled = (
                self.generate_solar_pdf_button.isEnabled()
            )
            self.generate_solar_pdf_button.setEnabled(False)

            temporary = directory / "pdf_request.tmp"
            temporary.write_text(request_id, encoding="utf-8")
            temporary.replace(request)

            self._pdf_diagnostic(
                f"13 ANDROID_REQUEST_PUBLISHED id={request_id}"
            )

            self._pdf_timer.start()

        except Exception as error:
            self._pdf_diagnostic(
                f"14 ANDROID_REQUEST_ERROR {type(error).__name__}: {error}"
            )

            # Detener cualquier temporizador que haya podido iniciarse.
            timer = getattr(self, "_pdf_timer", None)
            if timer is not None:
                timer.stop()

            # Eliminar únicamente el PDF temporal de esta operación.
            if output_path is not None:
                try:
                    output_path.unlink(missing_ok=True)
                except OSError as cleanup_error:
                    self._pdf_diagnostic(
                        f"14 ANDROID_PDF_CLEANUP_ERROR {cleanup_error}"
                    )

            # Eliminar el archivo provisional de publicación.
            if output_path is not None:
                temporary = output_path.parent / "pdf_request.tmp"
                try:
                    temporary.unlink(missing_ok=True)
                except OSError as cleanup_error:
                    self._pdf_diagnostic(
                        f"14 ANDROID_REQUEST_CLEANUP_ERROR {cleanup_error}"
                    )

            # Si la solicitud ya fue publicada, retirarla solamente
            # cuando todavía corresponde a esta operación.
            if output_path is not None:
                request_file = output_path.parent / "pdf_request.txt"
                try:
                    if (
                        request_file.is_file()
                        and request_file.read_text(
                            encoding="utf-8"
                        ).strip() == str(request_id)
                    ):
                        request_file.unlink(missing_ok=True)
                except (OSError, UnicodeError) as cleanup_error:
                    self._pdf_diagnostic(
                        f"14 ANDROID_PUBLISHED_CLEANUP_ERROR {cleanup_error}"
                    )

            self._pdf_request_id = None
            self._pdf_output_path = None

            self.generate_solar_pdf_button.setEnabled(
                getattr(
                    self,
                    "_pdf_button_was_enabled",
                    self.generate_solar_pdf_button.isEnabled(),
                )
            )

            QMessageBox.critical(
                self,
                "Error",
                f"No se ha podido iniciar la exportación PDF.\\n\\n{error}",
            )

    def _check_android_pdf_result(self):
        request_id = getattr(self, "_pdf_request_id", None)
        if request_id is None:
            return

        result = self._pdf_directory / "pdf_result.txt"

        if not result.is_file():
            return

        try:
            contents = result.read_text(encoding="utf-8")
            parts = contents.split("\n", 2)

            # No consumir respuestas incompletas.
            if len(parts) != 3:
                return

            received_id, status, detail = parts

            # No consumir respuestas de otras solicitudes.
            if received_id != request_id:
                return

            if status not in ("OK", "CANCELLED", "ERROR"):
                self._pdf_diagnostic(
                    f"17 ANDROID_UNKNOWN_STATUS {status}"
                )
                detail = (
                    f"Android ha devuelto un estado PDF "
                    f"desconocido: {status}. {detail}"
                )
                status = "ERROR"

            result.unlink(missing_ok=True)

            self._pdf_diagnostic(
                f"15 ANDROID_RESULT status={status} detail={detail}"
            )

            # Finalizar antes de mostrar cuadros de diálogo.
            self._pdf_timer.stop()

            output_path = getattr(self, "_pdf_output_path", None)
            if output_path is not None:
                output_path.unlink(missing_ok=True)

            self._pdf_output_path = None
            self._pdf_request_id = None

            self.generate_solar_pdf_button.setEnabled(
                getattr(self, "_pdf_button_was_enabled", True)
            )

            self._pdf_diagnostic("18 ANDROID_EXPORT_FINISHED")

            if status == "OK":
                QMessageBox.information(
                    self,
                    "Informe generado",
                    "El informe solar se ha guardado correctamente.",
                )

            elif status == "CANCELLED":
                self._pdf_diagnostic("16 ANDROID_EXPORT_CANCELLED")

            elif status == "ERROR":
                QMessageBox.critical(
                    self,
                    "Error",
                    f"No se ha podido guardar el informe PDF.\\n\\n{detail}",
                )

        except Exception as error:
            self._pdf_diagnostic(
                f"17 ANDROID_RESULT_ERROR {type(error).__name__}: {error}"
            )

            QMessageBox.critical(
                self,
                "Error",
                f"Error al procesar la exportación PDF.\\n\\n{error}",
            )

    # HELIOS_PDF_DIAG_END
