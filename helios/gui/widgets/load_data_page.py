from PySide6.QtCore import QEvent
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QFileDialog,
)

from pathlib import Path


from helios.utils.platform import is_android

class LoadDataPage(QWidget):

    def __init__(self, project, main_window):

        super().__init__()

        self.project = project
        self.main_window = main_window
        
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Archivo de consumo"))

        if is_android():
            row = QVBoxLayout()
        else:
            row = QHBoxLayout()

        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)
        if is_android():
            self.path_edit.setPlaceholderText(
                "Toca aquí para seleccionar un archivo Excel"
            )
            self.path_edit.installEventFilter(self)

        self.browse_button = QPushButton("Examinar...")

        row.addWidget(self.path_edit)
        if not is_android():
            row.addWidget(self.browse_button)
        else:
            self.browse_button.hide()

        layout.addLayout(row)

        self.load_button = QPushButton("Cargar")
        if is_android():
            self.load_button.setEnabled(False)

        layout.addWidget(self.load_button)

        self.info_label = QLabel("Ningún archivo cargado")
        self.info_label.setWordWrap(True)

        layout.addWidget(self.info_label)

        layout.addStretch()

        self.browse_button.clicked.connect(
            self.browse_file
        )

        self.load_button.clicked.connect(
            self.load_dataset
        )

    def eventFilter(self, watched, event):
        if (
            is_android()
            and watched is self.path_edit
            and event.type() == QEvent.Type.MouseButtonRelease
        ):
            if getattr(self, '_excel_request_id', None) is None:
                self.browse_file()
            return True
        return super().eventFilter(watched, event)

    def _update_android_load_button(self):
        if not is_android():
            return
        selected = getattr(self, '_excel_path', None)
        waiting = getattr(self, '_excel_request_id', None)
        self.load_button.setEnabled(
            waiting is None
            and selected is not None
            and Path(selected).is_file()
            and Path(selected).suffix.lower() == '.xlsx'
        )

    def browse_file(self):
        if not is_android():
            filename, _ = QFileDialog.getOpenFileName(
                self,
                "Seleccionar archivo de consumo",
                "",
                "Excel (*.xlsx)",
            )
            if filename:
                self.path_edit.setText(filename)
            return

        import os
        import uuid
        from PySide6.QtCore import QTimer

        if getattr(self, "_excel_request_id", None) is not None:
            return

        try:
            private = os.environ.get("ANDROID_PRIVATE")
            if not private:
                raise RuntimeError("ANDROID_PRIVATE no está definido")

            directory = Path(private) / "helios_excel"
            directory.mkdir(parents=True, exist_ok=True)

            request = directory / "excel_request.txt"
            result = directory / "excel_result.txt"

            request_id = str(uuid.uuid4())

            # Eliminar únicamente resultados de selecciones anteriores.
            result.unlink(missing_ok=True)

            self._excel_path = None
            self.path_edit.clear()
            self._excel_request_id = request_id
            self._excel_directory = directory

            self.browse_button.setEnabled(False)
            self.load_button.setEnabled(False)
            self.info_label.setText("Esperando selección de Excel...")

            if getattr(self, "_excel_timer", None) is None:
                self._excel_timer = QTimer(self)
                self._excel_timer.setInterval(300)
                self._excel_timer.timeout.connect(
                    self._check_android_excel_result
                )

            # Publicar la solicitud de forma atómica.
            temporary = directory / "excel_request.tmp"
            temporary.write_text(request_id, encoding="utf-8")
            temporary.replace(request)

            self._excel_timer.start()

        except Exception as exc:
            self._excel_request_id = None
            self.browse_button.setEnabled(True)
            self._update_android_load_button()
            self.info_label.setText(
                f"Error al abrir selector: {type(exc).__name__}: {exc}"
            )

    def _check_android_excel_result(self):
        request_id = getattr(self, "_excel_request_id", None)
        if request_id is None:
            return

        result = self._excel_directory / "excel_result.txt"

        if not result.is_file():
            return

        try:
            contents = result.read_text(encoding="utf-8")
            parts = contents.split("\n", 3)

            if len(parts) not in (3, 4):
                raise ValueError("Respuesta Android incompleta")

            received_id, status, detail = parts[:3]
            original_name = parts[3].strip() if len(parts) == 4 else ""

            if received_id != request_id:
                return

            result.unlink(missing_ok=True)

            if status == "OK":
                path = Path(detail.strip())

                if not path.is_file():
                    raise FileNotFoundError(str(path))

                if path.suffix.lower() != ".xlsx":
                    raise ValueError("El documento no es un archivo .xlsx")

                self._excel_path = str(path)
                display_name = Path(original_name).name if original_name else path.name
                self.path_edit.setText(display_name)
                self.info_label.setText(
                    "Excel seleccionado. Pulse Cargar."
                )

            elif status == "CANCELLED":
                self.info_label.setText("Selección cancelada.")

            elif status == "ERROR":
                self.info_label.setText(
                    f"Error al seleccionar Excel: {detail}"
                )

            else:
                raise ValueError(f"Estado Android desconocido: {status}")

        except Exception as exc:
            self._excel_path = None
            self.path_edit.clear()
            self.info_label.setText(
                f"Error de selección: {type(exc).__name__}: {exc}"
            )

        finally:
            # Solo finalizar cuando se haya recibido la respuesta
            # correspondiente a la solicitud actual.
            if not result.exists():
                self._excel_request_id = None
                self._excel_timer.stop()
                self.browse_button.setEnabled(True)
                self._update_android_load_button()

    def load_dataset(self):
        if self.project.solar_configuration is None:
            self.info_label.setText(
                "Debe guardar la configuración solar antes de cargar datos."
            )
            return

        path = getattr(self, "_excel_path", None) if is_android() else self.path_edit.text()

        if not path:

            self.info_label.setText(
                "Seleccione un archivo."
            )

            return

        try:

            self.project.load_data(path)

            self.project.analyze_data()

            # Un nuevo dataset invalida los resultados solares
            self.project.solar.reset()

            # Resetear también la interfaz solar
            self.main_window.solar_page.reset_results()

            self.update_project_info()

            self.main_window.set_project_loaded(True)

            self.main_window.update_project_pages()

            # Android: avanzar únicamente cuando el archivo
            # se haya cargado y analizado correctamente.
            if is_android():
                self.main_window.show_android_guided_navigation(
                    "Datos cargados correctamente",
                    "Optimización solar",
                )

        except Exception as e:

            import traceback

            traceback.print_exc()

            self.info_label.setText(
                f"Error: {type(e).__name__}: {e}"
            )

    def update_project_info(self):

        if self.project.dataset is None:

            self.info_label.setText("Ningún archivo cargado.")

            return

        dataset = self.project.dataset

        filename = self.path_edit.text() if is_android() else Path(self.path_edit.text()).name

        first = dataset.index.min().strftime("%d/%m/%Y")

        last = dataset.index.max().strftime("%d/%m/%Y")

        records = len(dataset)

        quality = self.project.quality

        from html import escape

        safe_filename = escape(str(filename))
        safe_rating = escape(str(quality["rating"]))

        self.info_label.setText(
            f"<b>Archivo:</b> {safe_filename}<br>"
            f"<b>Registros:</b> {records:,}"
            f" &nbsp;|&nbsp; "
            f"<b>Cobertura:</b> {quality['coverage']:.2f}%<br>"
            f"<b>Periodo:</b> {first} → {last}<br>"
            f"<b>Calidad:</b> {safe_rating}"
        )

    # ==================================================
    # Configuración solar
    # ==================================================

    def load_solar_configuration(self):

        configuration = self.project.solar_configuration

        if configuration is None:
            return

        self.latitude_spinbox.setValue(
            configuration.latitude
        )

        self.longitude_spinbox.setValue(
            configuration.longitude
        )

        self.tilt_spinbox.setValue(
            configuration.tilt
        )

        self.azimuth_spinbox.setValue(
            configuration.azimuth
        )

        self.system_losses_spinbox.setValue(
            configuration.losses
        )

        technology_index = (
            self.pv_technology_combobox.findData(
                configuration.pv_technology
            )
        )

        if technology_index >= 0:
            self.pv_technology_combobox.setCurrentIndex(
                technology_index
            )

        mounting_index = (
            self.mounting_place_combobox.findData(
                configuration.mounting_place
            )
        )

        if mounting_index >= 0:
            self.mounting_place_combobox.setCurrentIndex(
                mounting_index
            )

        self.solar_configuration_status.setText(
            "Configuración solar cargada."
        )