from PyQt5.QtWidgets import QWidget, QHBoxLayout, QCheckBox, QPushButton, QColorDialog
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QCursor, QColor
from controller.controller import Controller
from view.filter_menu import FilterMenu
from view.editable_label import EditableLabel
from model.filter import Filter


class FilterWidget(QWidget):
    def __init__(self, filter: Filter, parent=None):
        super().__init__(parent)

        self.controller: Controller = Controller()
        self.filter: Filter = filter

        self.create_ui()

    def create_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignVCenter)
        self.setLayout(layout)

        sub_layout = QHBoxLayout()
        sub_layout.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        layout.addLayout(sub_layout)

        self.checkbox = QCheckBox()
        self.checkbox.setToolTip("Show/Hide filter")
        self.checkbox.setChecked(True)
        self.checkbox.setCursor(QCursor(Qt.PointingHandCursor))
        self.checkbox.stateChanged.connect(
            lambda is_visible, filter=self.filter: self.controller.toggle_filter_visibility(
                filter, is_visible
            )
        )
        sub_layout.addWidget(self.checkbox)

        self.label = EditableLabel(self.filter.name)
        self.label.setMinimumWidth(130)
        self.label.setCursor(QCursor(Qt.PointingHandCursor))
        self.label.setToolTip(self.filter.name)
        self.label.confirm_text.connect(self.validate_filter_name)
        sub_layout.addWidget(self.label)

        self.color_btn = QPushButton()
        self.color_btn.setToolTip("Change filter color")
        self.color_btn.setFixedSize(20, 20)
        self.color_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.color_btn.setStyleSheet(
            f"""
                QPushButton {{
                    background-color: {self.filter.color};
                }}
                QToolTip {{
                    background-color: #ffffdc;
                    color: black;
                    border: 1px solid black;
                }}
            """
        )
        self.color_btn.clicked.connect(self.change_filter_color)
        sub_layout.addWidget(self.color_btn)

        self.edit_btn = QPushButton("⚙")
        self.edit_btn.setToolTip("Edit filter")
        self.edit_btn.setFixedSize(20, 20)
        self.edit_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.edit_btn.clicked.connect(
            lambda state, filter=self.filter: self.controller.edit_filter(filter)
        )
        layout.addWidget(self.edit_btn)

        self.delete_btn = QPushButton("X")
        self.delete_btn.setToolTip("Delete filter")
        self.delete_btn.setFixedSize(20, 20)
        self.delete_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.delete_btn.clicked.connect(
            lambda state, filter=self.filter: self.controller.delete_filter(filter)
        )
        layout.addWidget(self.delete_btn)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.filter_menu)

    def filter_menu(self, position: QPoint):
        menu = FilterMenu()

        menu.toggle_filter_visibility.connect(
            lambda is_visible=self.checkbox.isChecked(): self.checkbox.setChecked(
                not is_visible
            )
        )
        menu.rename_filter.connect(self.label.enter_edit_mode)
        menu.change_color_filter.connect(self.change_filter_color)
        menu.edit_filter.connect(
            lambda filter=self.filter: self.controller.edit_filter(filter)
        )
        menu.delete_filter.connect(
            lambda filter=self.filter: self.controller.delete_filter(filter)
        )

        menu.exec_(self.mapToGlobal(position))

    def validate_filter_name(self, text: str):
        is_confirmed = self.controller.rename_filter(self.filter, text)

        if is_confirmed:
            self.label.apply_validated_text()
            self.label.setToolTip(text)
        else:
            self.label.cancel_edit()

    def change_filter_color(self):
        color = QColorDialog.getColor(initial=QColor(self.filter.color), parent=self)

        if color.isValid():
            self.controller.set_filter_color(self.filter, color.name())
            self.color_btn.setStyleSheet(
                f"""
                    QPushButton {{
                        background-color: {self.filter.color};
                    }}
                    QToolTip {{
                        background-color: #ffffdc;
                        color: black;
                        border: 1px solid black;
                    }}
                """
            )
