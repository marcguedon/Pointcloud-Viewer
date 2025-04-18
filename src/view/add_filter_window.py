import pyvista as pv
from pyvistaqt import QtInteractor
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QColor, QCursor
from PyQt5.QtCore import Qt


class AddFilterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.filter_name = ""
        self.filter_bounds = ()
        self.filter_color = QColor("black")

        self.coord_inputs = {}

        self.setWindowTitle("Add Filter")

        self.create_ui()

    def create_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        parameters_layout = QHBoxLayout()
        main_layout.addLayout(parameters_layout)

        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(5, 20, 20, 20)
        left_layout.setSpacing(10)
        parameters_layout.addLayout(left_layout)

        # Filter name
        name_layout = QVBoxLayout()
        name_layout.setSpacing(0)
        left_layout.addLayout(name_layout)

        name_label = QLabel("Filter Name:")
        name_layout.addWidget(name_label)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter filter name")
        self.name_edit.textChanged.connect(self.validate)
        name_layout.addWidget(self.name_edit)

        # Filter coordinates
        for label in ["X min", "X max", "Y min", "Y max", "Z min", "Z max"]:
            spin = QDoubleSpinBox()
            spin.setRange(-1000, 1000)
            spin.setDecimals(2)
            spin.setSingleStep(0.1)

            if "min" in label:
                spin.setValue(0.0)

            else:
                spin.setValue(1.0)

            spin.valueChanged.connect(self.update_preview)
            self.coord_inputs[label] = spin
            layout = QVBoxLayout()
            layout.setSpacing(0)
            layout.addWidget(QLabel(label))
            layout.addWidget(spin)
            left_layout.addLayout(layout)

        # Filter color
        color_layout = QHBoxLayout()
        color_layout.setSpacing(0)
        left_layout.addLayout(color_layout)

        color_label = QLabel("Filter Color:")
        color_layout.addWidget(color_label)

        self.color_button = QPushButton()
        # TODO Problème: Tooltip takes the color background of the button
        # self.color_button.setToolTip("Choose filter color")
        self.color_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.color_button.setFixedSize(40, 20)
        self.color_button.setStyleSheet(
            f"background-color: {self.filter_color.name()};"
        )
        self.color_button.clicked.connect(self.choose_color)
        color_layout.addWidget(self.color_button)

        # Display filter
        self.plotter_widget = QtInteractor(self)
        parameters_layout.addWidget(self.plotter_widget)
        self.update_preview()

        # Cancel/Add buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(30, 30, 30, 30)
        buttons_layout.setSpacing(50)
        main_layout.addLayout(buttons_layout)

        cancel_button = QPushButton("Cancel")
        cancel_button.setToolTip("Cancel")
        cancel_button.setCursor(QCursor(Qt.PointingHandCursor))
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)

        self.add_button = QPushButton("Add")
        self.add_button.setToolTip("Add filter")
        self.add_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.add_button.clicked.connect(self.accept)
        self.add_button.setEnabled(False)
        buttons_layout.addWidget(self.add_button)

    def choose_color(self):
        color = QColorDialog.getColor(initial=self.filter_color, parent=self)

        if color.isValid():
            self.filter_color = color
            self.color_button.setStyleSheet(
                f"background-color: {self.filter_color.name()};"
            )
            self.update_preview()

    def validate(self):
        name_filled = self.name_edit.text() != ""
        self.add_button.setEnabled(name_filled)

    def accept(self):
        self.filter_name = self.name_edit.text()
        self.filter_bounds = (
            self.coord_inputs["X min"].value(),
            self.coord_inputs["X max"].value(),
            self.coord_inputs["Y min"].value(),
            self.coord_inputs["Y max"].value(),
            self.coord_inputs["Z min"].value(),
            self.coord_inputs["Z max"].value(),
        )
        self.filter_color = self.filter_color

        super().accept()

    def update_preview(self):
        self.plotter_widget.clear()
        bounds = (
            self.coord_inputs["X min"].value(),
            self.coord_inputs["X max"].value(),
            self.coord_inputs["Y min"].value(),
            self.coord_inputs["Y max"].value(),
            self.coord_inputs["Z min"].value(),
            self.coord_inputs["Z max"].value(),
        )
        box = pv.Box(bounds=bounds)
        self.plotter_widget.add_mesh(
            box, style="wireframe", color=self.filter_color.name(), line_width=3
        )
