from view.editable_label import EditableLabel
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QCursor


class FilterWidget(QWidget):
    visibility_changed = pyqtSignal(bool)
    name_changed = pyqtSignal(str)
    edit_requested = pyqtSignal()
    delete_requested = pyqtSignal()

    def __init__(self, name, parent=None):
        super().__init__(parent)

        self.name = name

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
            lambda state: self.visibility_changed.emit(state)
        )
        sub_layout.addWidget(self.checkbox)

        self.label = EditableLabel(self.name)
        self.label.setMinimumWidth(150)
        self.label.text_confirmed.connect(lambda text: self.name_changed.emit(text))
        self.label.setCursor(QCursor(Qt.PointingHandCursor))
        self.label.setToolTip(self.name)
        sub_layout.addWidget(self.label)

        self.edit_btn = QPushButton("⚙")
        self.edit_btn.setToolTip("Edit filter")
        self.edit_btn.setFixedSize(20, 20)
        self.edit_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.edit_btn.clicked.connect(lambda state: self.edit_requested.emit())
        layout.addWidget(self.edit_btn)

        self.delete_btn = QPushButton("X")
        self.delete_btn.setToolTip("Delete filter")
        self.delete_btn.setFixedSize(20, 20)
        self.delete_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.delete_btn.clicked.connect(lambda state: self.delete_requested.emit())
        layout.addWidget(self.delete_btn)

    def set_name(self, name):
        self.name = name
        self.label.apply_validated_text(name)
        self.label.setToolTip(name)

    def set_visibility(self, visible):
        self.checkbox.setChecked(visible)
