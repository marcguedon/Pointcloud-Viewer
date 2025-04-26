from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from view.viewer_layout import ViewerLayout
from model.filter import Filter
from view.filter_window import FilterDialog


class ViewerArea(QMdiArea):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setViewMode(QMdiArea.SubWindowView)
        self.setOption(QMdiArea.DontMaximizeSubWindowOnActivation, True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.viewer_subwindow = QMdiSubWindow()
        self.viewer_subwindow.setWindowFlags(Qt.FramelessWindowHint)
        self.viewer_subwindow.setAttribute(Qt.WA_DeleteOnClose, False)

        self.viewer_layout = ViewerLayout()
        viewer_widget = QWidget()
        viewer_widget.setLayout(self.viewer_layout)
        self.viewer_subwindow.setWidget(viewer_widget)

        self.addSubWindow(self.viewer_subwindow)

        self.viewer_subwindow.showMaximized()

    def show_filter_dialog(self, filter: Filter):
        sub = FilterDialog(self, filter)
        self.addSubWindow(sub)
        sub.show()

    def add_pointcloud(self, name: str, data):
        self.viewer_layout.add_pointcloud(name, data)

    def delete_pointcloud(self, name: str):
        self.viewer_layout.delete_pointcloud(name)

    def change_pointcloud_name(self, old_name: str, new_name: str):
        self.viewer_layout.change_pointcloud_name(old_name, new_name)

    def add_filter(self, name: str, data, color: str):
        self.viewer_layout.add_filter(name, data, color)

    def delete_filter(self, name: str):
        self.viewer_layout.delete_filter(name)

    def change_filter_name(self, old_name: str, new_name: str):
        self.viewer_layout.change_filter_name(old_name, new_name)

    def change_theme(self):
        self.viewer_layout.change_theme()

    def show_hide_axes(self):
        self.viewer_layout.show_hide_axes()
