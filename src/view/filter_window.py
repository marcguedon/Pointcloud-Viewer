from PyQt5.QtWidgets import *
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt, QEvent
from model.filter import Filter
from controller.controller import Controller


# TODO: Manage filter name change
class FilterDialog(QMdiSubWindow):
    def __init__(self, parent, filter: Filter):
        super().__init__()

        self.parent = parent
        self.controller = Controller()

        self.is_collapsed = False
        self.title_bar_height = self.style().pixelMetric(QStyle.PM_TitleBarHeight)

        self.filter_name = filter.name
        self.filter_bounds = filter.box.bounds
        self.filter_color = filter.color

        self.coord_inputs = {}

        self.setWindowTitle("Edit Filter")
        self.setWindowFlags(
            Qt.WindowCloseButtonHint
            | Qt.WindowMinimizeButtonHint
            | Qt.WindowStaysOnTopHint  # TODO: To remove from title bar menu
            | Qt.MSWindowsFixedSizeDialogHint
        )

        self.normal_size = None
        self.create_ui()

        # self.is_dragging = False
        # self.drag_start_pos = None

    def create_ui(self):
        main_widget = QWidget()
        self.setWidget(main_widget)

        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        parameters_layout = QHBoxLayout()
        main_layout.addLayout(parameters_layout)

        left_layout = QVBoxLayout()
        left_layout.setSpacing(10)
        parameters_layout.addLayout(left_layout)

        # Filter coordinates
        for label, value in zip(
            ["X min", "X max", "Y min", "Y max", "Z min", "Z max"], self.filter_bounds
        ):
            spin = QDoubleSpinBox()
            spin.setToolTip(f"Enter {label.lower()} coordinate")
            spin.setRange(-1000, 1000)
            spin.setDecimals(2)
            spin.setSingleStep(0.1)
            spin.setValue(value)
            spin.valueChanged.connect(self.update_viewer)
            self.coord_inputs[label] = spin
            layout = QVBoxLayout()
            layout.setSpacing(0)
            layout.addWidget(QLabel(label))
            layout.addWidget(spin)
            left_layout.addLayout(layout)

        # Filter color
        color_layout = QHBoxLayout()
        color_layout.setSpacing(5)
        left_layout.addLayout(color_layout)

        color_label = QLabel("Filter Color:")
        color_layout.addWidget(color_label)

        self.color_button = QPushButton()
        self.color_button.setToolTip("Choose filter color")
        self.color_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.color_button.setFixedSize(40, 20)
        self.color_button.setStyleSheet(
            f"""
                QPushButton {{
                    background-color: {self.filter_color.name()};
                }}
                QToolTip {{
                    background-color: #ffffdc;
                    color: black;
                    border: 1px solid black;
                }}
            """
        )
        self.color_button.clicked.connect(self.choose_color)
        color_layout.addWidget(self.color_button)

        self.normal_size = self.sizeHint()

    def choose_color(self):
        color = QColorDialog.getColor(initial=self.filter_color, parent=self)

        if color.isValid():
            self.filter_color = color
            self.color_button.setStyleSheet(
                f"""
                    QPushButton {{
                        background-color: {self.filter_color.name()};
                    }}
                    QToolTip {{
                        background-color: #ffffdc;
                        color: black;
                        border: 1px solid black;
                    }}
                """
            )

            self.update_viewer()

    def update_viewer(self):
        self.controller.set_filter_bounds(
            self.filter_name,
            (
                self.coord_inputs["X min"].value(),
                self.coord_inputs["X max"].value(),
                self.coord_inputs["Y min"].value(),
                self.coord_inputs["Y max"].value(),
                self.coord_inputs["Z min"].value(),
                self.coord_inputs["Z max"].value(),
            ),
        )
        self.controller.set_filter_color(self.filter_name, self.filter_color)
        self.parent.delete_filter(self.filter_name)
        self.parent.add_filter(
            self.filter_name,
            self.controller.get_filter_by_name(self.filter_name).box,
            self.filter_color.name(),
        )

    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange:
            if self.windowState():
                self.handle_minimize()

        event.accept()

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
            )  # TODO: height doesn't work as expected

    def mouseDoubleClickEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.handle_minimize()

        event.accept()

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

    # def closeEvent(self, event):
    #     """ Gestion de la fermeture de la fenêtre (clique sur le bouton Close) """
    #     # Tu peux faire des actions supplémentaires ici avant de fermer la fenêtre si nécessaire
    #     self.setWindowFlags(
    #         Qt.WindowCloseButtonHint
    #         | Qt.WindowMinimizeButtonHint
    #         | Qt.WindowStaysOnTopHint
    #         | Qt.MSWindowsFixedSizeDialogHint
    #     )
    #     event.accept()

    # def showMinimized(self):
    #     """ Quand on appuie sur le bouton Minimize """
    #     self.is_collapsed = True
    #     self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMaximizeButtonHint)
    #     self.resize(self.width(), self.title_bar_height)
    #     super().showMinimized()

    # def showNormal(self):
    #     """ Quand on appuie sur le bouton Restore ou Maximize """
    #     self.is_collapsed = False
    #     self.setWindowFlags(
    #         Qt.WindowCloseButtonHint
    #         | Qt.WindowMinimizeButtonHint
    #         | Qt.WindowStaysOnTopHint
    #         | Qt.MSWindowsFixedSizeDialogHint
    #     )
    #     super().showNormal()
