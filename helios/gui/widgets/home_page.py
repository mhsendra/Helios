from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout


class HomePage(QWidget):

    def __init__(self, project):

        super().__init__()

        self.project = project

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Página principal"))