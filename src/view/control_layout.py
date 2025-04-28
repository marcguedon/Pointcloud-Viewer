from PyQt5.QtWidgets import QFrame, QVBoxLayout, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from controller.controller import Controller
from view.pointclouds_layout import PointcloudsLayout
from view.filters_layout import FiltersLayout


class ControlLayout(QVBoxLayout):
    def __init__(self):
        super().__init__()

        self.controller = Controller()

        self.create_ui()

    def create_ui(self):
        self.setSpacing(10)

        pointcloud_layout = PointcloudsLayout()
        self.addLayout(pointcloud_layout)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        self.addWidget(separator)

        # Filters
        filters_layout = FiltersLayout()
        self.addLayout(filters_layout)

        # Quit button
        quit_btn = QPushButton("Quit")
        quit_btn.setToolTip("Quit application")
        quit_btn.setCursor(QCursor(Qt.PointingHandCursor))
        quit_btn.clicked.connect(self.controller.close_application)
        self.addWidget(quit_btn)
