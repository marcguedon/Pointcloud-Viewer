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
from PyQt5.QtCore import Qt, pyqtSignal
from controller.controller import Controller
from model.filter import Filter


class EditFilterWindow(QMdiSubWindow):
    closed = pyqtSignal(Filter)

    def __init__(self, filter: Filter):
        super().__init__()

        self.controller = Controller()
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
            | Qt.WindowStaysOnTopHint  # TODO: To remove from title bar menu
            | Qt.MSWindowsFixedSizeDialogHint
        )
        self.setAttribute(Qt.WA_DeleteOnClose, True)

        self.normal_size = None
        self.create_ui()

        # self.is_dragging = False
        # self.drag_start_pos = None

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
            font = spin.font()
            font.setPointSize(8)
            spin.setFont(font)
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

        self.normal_size = self.sizeHint()

    def closeEvent(self, event):
        self.closed.emit(self.current_filter)
        super().closeEvent(event)

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
            self.resize(self.width(), self.title_bar_height)

        else:
            self.setWindowFlags(
                Qt.WindowCloseButtonHint
                | Qt.WindowMinimizeButtonHint
                | Qt.WindowStaysOnTopHint
                | Qt.MSWindowsFixedSizeDialogHint
            )
            self.resize(
                self.width(), self.normal_size.height()
            )  # TODO: Height doesn't work as expected

    def mouseDoubleClickEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.handle_minimize()

        event.accept()

    # NECESSARY to override the minimize/maximize button
    # def changeEvent(self, event):
    #     if event.type() == QEvent.WindowStateChange:
    #         if self.windowState():
    #             self.handle_minimize()

    #     event.accept()

    # def mousePressEvent(self, event):
    #     if event.button() == Qt.LeftButton:
    #         self.is_dragging = True
    #         self.drag_start_pos = event.globalPos()  # Position initiale de la souris

    #     event.accept()

    # def mouseMoveEvent(self, event):
    #     if self.is_dragging:
    #         # Déplacer la fenêtre sans changer l'état de la taille
    #         delta = event.globalPos() - self.drag_start_pos
    #         self.move(self.pos() + delta)
    #         self.drag_start_pos = (
    #             event.globalPos()
    #         )  # Mettre à jour la position de départ

    #     event.accept()

    # def mouseReleaseEvent(self, event):
    #     if event.button() == Qt.LeftButton:
    #         self.is_dragging = False

    #     event.accept()

    # def showMinimized(self):
    #     print("showMinimized")
    #     self.is_collapsed = True
    #     self.setWindowFlags(
    #         Qt.WindowCloseButtonHint
    #         | Qt.WindowMaximizeButtonHint
    #         | Qt.WindowStaysOnTopHint
    #         | Qt.MSWindowsFixedSizeDialogHint
    #     )
    #     self.resize(self.width(), self.title_bar_height)
    #     super().showMinimized()

    # def showNormal(self):
    #     print("showNormal")
    #     self.is_collapsed = False
    #     self.setWindowFlags(
    #         Qt.WindowCloseButtonHint
    #         | Qt.WindowMinimizeButtonHint
    #         | Qt.WindowStaysOnTopHint
    #         | Qt.MSWindowsFixedSizeDialogHint
    #     )
    #     super().showNormal()
