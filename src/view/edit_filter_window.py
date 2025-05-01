from PyQt5.QtWidgets import (
    QWidget,
    QMdiSubWindow,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QDoubleSpinBox,
    QStyle,
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSignal, QEvent
from controller.controller import Controller
from model.filter import Filter


# TODO: Minimize/maximize event are still bugging
# TODO: Move action in the menu does not work
# TODO: Remove Stay on Top action from the menu
class EditFilterWindow(QMdiSubWindow):
    closed = pyqtSignal(Filter)

    def __init__(self, filter: Filter):
        super().__init__()

        self.controller: Controller = Controller()
        self.controller.update_filter_signal.connect(
            lambda filter: self.setWindowTitle(f"Edit Filter: {filter.name}")
        )

        self.is_changing_filter = False
        self.is_collapsed = False
        self.title_bar_height = self.style().pixelMetric(QStyle.PM_TitleBarHeight)

        self.current_filter = filter

        self.coord_inputs = {}

        self.setWindowTitle(f"Edit Filter: {self.current_filter.name}")
        self.setWindowFlags(
            Qt.WindowCloseButtonHint
            | Qt.WindowMinimizeButtonHint
            | Qt.WindowStaysOnTopHint
            | Qt.MSWindowsFixedSizeDialogHint
        )
        self.setAttribute(Qt.WA_DeleteOnClose, True)

        self.normal_size = None
        self.create_ui()

    def create_ui(self):
        main_widget = QWidget()
        self.setWidget(main_widget)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(8)
        main_widget.setLayout(main_layout)

        first_line_layout = QHBoxLayout()
        second_line_layout = QHBoxLayout()

        labels = ["X min", "X max", "Y min", "Y max", "Z min", "Z max"]
        bounds = self.current_filter.box.bounds

        for i, (bound_label, value) in enumerate(zip(labels, bounds)):
            spin = QDoubleSpinBox()
            spin.setFixedHeight(20)
            spin.setFont(QFont("Arial", 10))
            spin.setToolTip(f"Enter {bound_label.lower()} coordinate")
            spin.setRange(-1000, 1000)
            spin.setDecimals(2)
            spin.setSingleStep(0.1)
            spin.setValue(value)
            spin.valueChanged.connect(self.update_viewer)
            self.coord_inputs[bound_label] = spin

            layout = QVBoxLayout()
            layout.setSpacing(0)

            label = QLabel(bound_label)
            label.setFont(QFont("Arial", 10))
            layout.addWidget(label)
            layout.addWidget(spin)

            if i % 2 == 0:
                first_line_layout.addLayout(layout)
            else:
                second_line_layout.addLayout(layout)

        main_layout.addLayout(first_line_layout)
        main_layout.addLayout(second_line_layout)

        self.normal_height = self.sizeHint().height()

    def closeEvent(self, event):
        self.closed.emit(self.current_filter)
        super().closeEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.handle_minimize()

        event.accept()

    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange:
            if self.windowState():
                self.handle_minimize()

        event.accept()

    def change_current_filter(self, filter: Filter):
        self.current_filter = filter
        self.setWindowTitle(f"Edit Filter: {self.current_filter.name}")

        self.is_changing_filter = True

        for label, value in zip(
            ["X min", "X max", "Y min", "Y max", "Z min", "Z max"],
            self.current_filter.box.bounds,
        ):
            self.coord_inputs[label].setValue(value)

        self.is_changing_filter = False

    def update_viewer(self):
        if self.is_changing_filter:
            return

        self.controller.set_filter_bounds(
            self.current_filter,
            (
                self.coord_inputs["X min"].value(),
                self.coord_inputs["X max"].value(),
                self.coord_inputs["Y min"].value(),
                self.coord_inputs["Y max"].value(),
                self.coord_inputs["Z min"].value(),
                self.coord_inputs["Z max"].value(),
            ),
        )

    def handle_minimize(self):
        self.is_collapsed = not self.is_collapsed
        self.showNormal()

        if self.is_collapsed:
            self.setWindowFlags(
                Qt.WindowCloseButtonHint
                | Qt.WindowMaximizeButtonHint
                | Qt.WindowStaysOnTopHint
                | Qt.MSWindowsFixedSizeDialogHint
            )
            self.setFixedHeight(self.title_bar_height)
        else:
            self.setWindowFlags(
                Qt.WindowCloseButtonHint
                | Qt.WindowMinimizeButtonHint
                | Qt.WindowStaysOnTopHint
                | Qt.MSWindowsFixedSizeDialogHint
            )
            self.setFixedHeight(self.normal_height + self.title_bar_height)
