DARK_STYLE = """

/* ==========================================================
   TEMA OSCURO PROFESIONAL — HELIOS ANALYTICS
   ========================================================== */

QWidget {
    background-color: #1E1E1E;
    color: #E0E0E0;
    font-family: "Segoe UI", sans-serif;
    font-size: 11pt;
}

/* ----------------------------------------------------------
   TABS
   ---------------------------------------------------------- */

QTabWidget::pane {
    border: 1px solid #3A3A3A;
    background: #1E1E1E;
}

QTabBar::tab {
    background: #2A2A2A;
    color: #CCCCCC;
    padding: 8px 18px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}

QTabBar::tab:selected {
    background: #3A3A3A;
    color: #FFFFFF;
    font-weight: bold;
}

QTabBar::tab:hover {
    background: #444444;
}

/* ----------------------------------------------------------
   GROUP BOXES
   ---------------------------------------------------------- */

QGroupBox {
    border: 1px solid #3A3A3A;
    border-radius: 6px;
    margin-top: 12px;
    padding: 10px;
    font-weight: bold;
    color: #FFFFFF;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 4px 8px;
    background-color: #2A2A2A;
    border-radius: 4px;
}

/* ----------------------------------------------------------
   LABELS
   ---------------------------------------------------------- */

QLabel {
    color: #E0E0E0;
}

QLabel[role="value"] {
    font-size: 12pt;
    font-weight: bold;
    color: #FFFFFF;
}

/* ----------------------------------------------------------
   LISTAS HTML (anomalías, insights)
   ---------------------------------------------------------- */

QLabel {
    font-size: 11pt;
}

ul {
    margin-left: 12px;
    padding-left: 0px;
}

li {
    margin-bottom: 4px;
    color: #D0D0D0;
}

/* ----------------------------------------------------------
   FORM LAYOUT
   ---------------------------------------------------------- */

QFormLayout::item {
    padding: 4px;
}

/* ----------------------------------------------------------
   SCROLL AREAS
   ---------------------------------------------------------- */

QScrollArea {
    background-color: #1E1E1E;
    border: none;
}

QScrollBar:vertical {
    background: #2A2A2A;
    width: 12px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #555555;
    min-height: 20px;
    border-radius: 6px;
}

QScrollBar::handle:vertical:hover {
    background: #777777;
}

QScrollBar::add-line,
QScrollBar::sub-line {
    background: none;
    height: 0px;
}

/* ----------------------------------------------------------
   BOTONES (si los usas en otras páginas)
   ---------------------------------------------------------- */

QPushButton {
    background-color: #2D2D2D;
    color: #FFFFFF;
    padding: 6px 14px;
    border-radius: 6px;
    border: 1px solid #444444;
}

QPushButton:hover {
    background-color: #3A3A3A;
}

QPushButton:pressed {
    background-color: #555555;
}

/* ----------------------------------------------------------
   CAMPOS DE TEXTO
   ---------------------------------------------------------- */

QLineEdit, QTextEdit {
    background-color: #2A2A2A;
    color: #FFFFFF;
    border: 1px solid #444444;
    border-radius: 4px;
    padding: 4px;
}

QLineEdit:focus, QTextEdit:focus {
    border: 1px solid #777777;
}

/* ----------------------------------------------------------
   COMBOBOX
   ---------------------------------------------------------- */

QComboBox {
    background-color: #2A2A2A;
    color: #FFFFFF;
    padding: 4px;
    border: 1px solid #444444;
    border-radius: 4px;
}

QComboBox QAbstractItemView {
    background-color: #2A2A2A;
    color: #FFFFFF;
    selection-background-color: #444444;
}

/* ----------------------------------------------------------
   TABLES (si las usas en otras páginas)
   ---------------------------------------------------------- */

QTableWidget {
    background-color: #1E1E1E;
    gridline-color: #3A3A3A;
    color: #FFFFFF;
}

QHeaderView::section {
    background-color: #2A2A2A;
    color: #FFFFFF;
    padding: 6px;
    border: none;
}

QTableWidget::item:selected {
    background-color: #444444;
}
"""