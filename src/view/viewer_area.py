from PyQt5.QtWidgets import QWidget, QMdiArea, QMdiSubWindow
from PyQt5.QtCore import Qt
from controller.controller import Controller
from view.viewer_layout import ViewerLayout
from view.edit_filter_window import EditFilterWindow
from view.socket_window import SocketWindow
from view.debug_window import DebugWindow
from model.filter import Filter


class ViewerArea(QMdiArea):
    def __init__(self):
        super().__init__()

        self.controller: Controller = Controller()
        self.controller.edit_filter_signal.connect(self.show_edit_filter_window)
        self.controller.delete_filter_signal.connect(self.close_edit_filter_window)
        self.controller.open_socket_window_signal.connect(self.open_socket_window)
        self.controller.open_debug_window_signal.connect(self.open_debug_window)

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

        self.edit_filter_window: EditFilterWindow = None
        self.socket_window: SocketWindow = None
        self.debug_window: DebugWindow = None

    def show_edit_filter_window(self, filter: Filter):
        if self.edit_filter_window is None:
            self.edit_filter_window = EditFilterWindow(filter)
            self.edit_filter_window.closed.connect(self.close_edit_filter_window)
            self.addSubWindow(self.edit_filter_window)
            self.edit_filter_window.show()

        else:
            self.edit_filter_window.change_current_filter(filter)
            self.edit_filter_window.setFocus()
            self.edit_filter_window.raise_()

    def close_edit_filter_window(self, filter: Filter):
        if self.edit_filter_window is not None:
            if self.edit_filter_window.current_filter == filter:
                self.edit_filter_window.close()
                self.edit_filter_window = None

    def open_socket_window(self):
        if self.socket_window is None:
            self.socket_window = SocketWindow()
            self.socket_window.closed.connect(self.close_socket_window)
            self.addSubWindow(self.socket_window)
            self.socket_window.show()
        else:
            self.socket_window.setFocus()
            self.socket_window.raise_()

    def close_socket_window(self):
        if self.socket_window is not None:
            self.socket_window.close()
            self.socket_window = None

    def open_debug_window(self):
        if self.debug_window is None:
            self.debug_window = DebugWindow()
            self.debug_window.closed.connect(self.close_debug_window)
            self.addSubWindow(self.debug_window)
            self.debug_window.show()
        else:
            self.debug_window.setFocus()
            self.debug_window.raise_()

    def close_debug_window(self):
        if self.debug_window is not None:
            self.debug_window.close()
            self.debug_window = None
