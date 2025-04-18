from PyQt5.QtWidgets import QMenu, QAction
from PyQt5.QtCore import pyqtSignal


class PointcloudMenu(QMenu):
    toggle_pointcloud_visibility = pyqtSignal()
    rename_pointcloud = pyqtSignal()
    delete_pointcloud = pyqtSignal()

    def __init__(self):
        super().__init__()

        visibility_action = QAction("Toggle visibility", self)
        visibility_action.triggered.connect(self.toggle_pointcloud_visibility)
        self.addAction(visibility_action)

        rename_action = QAction("Rename", self)
        rename_action.triggered.connect(self.rename_pointcloud)
        self.addAction(rename_action)

        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(self.delete_pointcloud)
        self.addAction(delete_action)
