from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QCursor
from view.editable_label import EditableLabel
from model.pointcloud import Pointcloud
from view.pointcloud_menu import PointcloudMenu
from controller.controller import Controller


class PointcloudWidget(QWidget):
    def __init__(self, pointcloud: Pointcloud):
        super().__init__()

        self.controller: Controller = Controller()
        self.pointcloud: Pointcloud = pointcloud

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
        self.checkbox.setToolTip("Show/Hide pointcloud")
        self.checkbox.setChecked(True)
        self.checkbox.setCursor(QCursor(Qt.PointingHandCursor))
        self.checkbox.stateChanged.connect(
            lambda is_visible, pointcloud=self.pointcloud: self.controller.toggle_pointcloud_visibility(
                pointcloud, is_visible
            )
        )
        sub_layout.addWidget(self.checkbox)

        self.label = EditableLabel(self.pointcloud.name)
        self.label.setMinimumWidth(180)
        self.label.setCursor(QCursor(Qt.PointingHandCursor))
        self.label.setToolTip(self.pointcloud.name)
        self.label.confirm_text.connect(self.validate_pointcloud_name)
        sub_layout.addWidget(self.label)

        self.delete_btn = QPushButton("X")
        self.delete_btn.setToolTip("Delete pointcloud")
        self.delete_btn.setFixedSize(20, 20)
        self.delete_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.delete_btn.clicked.connect(
            lambda state, pointcloud=self.pointcloud: self.controller.delete_pointcloud(
                pointcloud
            )
        )
        layout.addWidget(self.delete_btn)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.pointcloud_menu)

    def pointcloud_menu(self, position: QPoint):
        menu = PointcloudMenu()

        menu.toggle_pointcloud_visibility.connect(
            lambda is_visible=self.checkbox.isChecked(): self.checkbox.setChecked(
                not is_visible
            )
        )
        menu.rename_pointcloud.connect(self.label.enter_edit_mode)
        menu.delete_pointcloud.connect(
            lambda pointcloud=self.pointcloud: self.controller.delete_pointcloud(
                pointcloud
            )
        )

        menu.exec_(self.mapToGlobal(position))

    def validate_pointcloud_name(self, text: str):
        is_confirmed = self.controller.rename_pointcloud(self.pointcloud, text)

        if is_confirmed:
            self.label.apply_validated_text()
            self.label.setToolTip(text)
        else:
            self.label.cancel_edit()
