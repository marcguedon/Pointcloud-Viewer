from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from controller.controller import Controller
from view.viewer_layout import ViewerLayout
from model.filter import Filter
from view.filter_window import FilterDialog


# TODO: Rework the filter window management
class ViewerArea(QMdiArea):
    def __init__(self):
        super().__init__()

        self.controller = Controller()
        self.controller.edit_filter_signal.connect(self.show_filter_dialog)
        self.controller.delete_filter_signal.connect(self.close_filter_dialog)

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

        self.filter_dialog = None

    def show_filter_dialog(self, filter: Filter):
        if self.filter_dialog is None:
            self.filter_dialog = FilterDialog(filter)
            self.addSubWindow(self.filter_dialog)
            self.filter_dialog.show()

        else:
            self.filter_dialog.change_current_filter(filter)
            self.filter_dialog.setFocus()
            self.filter_dialog.raise_()

    def close_filter_dialog(self, filter: Filter):
        if self.filter_dialog is not None:
            if self.filter_dialog.current_filter == filter:
                self.filter_dialog.close()
                self.filter_dialog = None
