from PyQt5.QtWidgets import QMenu, QAction
from PyQt5.QtCore import pyqtSignal


class FilterMenu(QMenu):
    toggle_filter_visibility = pyqtSignal()
    rename_filter = pyqtSignal()
    change_color_filter = pyqtSignal()
    edit_filter = pyqtSignal()
    delete_filter = pyqtSignal()

    def __init__(self):
        super().__init__()

        visibility_action = QAction("Toggle visibility", self)
        visibility_action.triggered.connect(self.toggle_filter_visibility)
        self.addAction(visibility_action)

        rename_action = QAction("Rename", self)
        rename_action.triggered.connect(self.rename_filter)
        self.addAction(rename_action)

        change_color_action = QAction("Change color", self)
        change_color_action.triggered.connect(self.change_color_filter)
        self.addAction(change_color_action)

        edit_action = QAction("Edit bounds", self)
        edit_action.triggered.connect(self.edit_filter)
        self.addAction(edit_action)

        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(self.delete_filter)
        self.addAction(delete_action)
