import qdarkstyle
from PyQt5.QtWidgets import (
    QWidget,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QMenuBar,
    QAction,
    QPushButton,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCloseEvent
from controller.controller import Controller
from view.control_layout import ControlLayout
from view.viewer_area import ViewerArea
from view.help_window import HelpWindow
from utils.log import Log
from utils.theme import Theme


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.controller: Controller = Controller()
        self.controller.notify_signal.connect(self.on_notify_signal)
        self.controller.close_application_signal.connect(self.close)
        self.controller.change_theme_signal.connect(self.change_theme)

        self.setWindowTitle("Pointclouds Viewer")
        self.resize(1920, 1080)

        self.help_window = None

        self.create_ui()

    def create_ui(self):
        window_widget = QWidget()
        self.setCentralWidget(window_widget)

        main_layout = QVBoxLayout()
        window_widget.setLayout(main_layout)

        sub_main_layout = QHBoxLayout()
        main_layout.addLayout(sub_main_layout)

        self.control_layout = ControlLayout()
        sub_main_layout.addLayout(self.control_layout)

        self.viewer_area = ViewerArea()
        sub_main_layout.addWidget(self.viewer_area, stretch=1)

        info_layout = QHBoxLayout()
        main_layout.addLayout(info_layout)

        info_layout.addWidget(QLabel("INFO: "))

        self.info_label = QLabel("")
        self.info_label.setObjectName("info_label")
        info_layout.addWidget(self.info_label)

        info_layout.addStretch()

        open_debug_window_button = QPushButton("…")
        open_debug_window_button.setCursor(Qt.PointingHandCursor)
        open_debug_window_button.setToolTip("Open debug window")
        open_debug_window_button.setFixedSize(20, 20)
        open_debug_window_button.clicked.connect(self.controller.open_debug_window)
        info_layout.addWidget(open_debug_window_button)

        self.create_menu()

    def create_menu(self):
        menu_bar = QMenuBar()
        self.setMenuBar(menu_bar)

        file_menu = menu_bar.addMenu("&Data")
        file_menu.setCursor(Qt.PointingHandCursor)
        file_menu.addAction("Load pointclouds", self.controller.load_pointcloud_files)
        file_menu.addAction("Open socket window", self.controller.open_socket_window)
        file_menu.addSeparator()
        file_menu.addAction("Add Filter", self.controller.add_filter)
        file_menu.addSeparator()
        file_menu.addAction("Quit", self.controller.close_application)

        # edit_menu = menu_bar.addMenu("&Edit")
        # edit_menu.setCursor(Qt.PointingHandCursor)
        # edit_menu.addAction("Add Filter", self.on_add_filter_button_clicked)
        # edit_menu.addAction("Remove Filter", self.on_add_filter_button_clicked)
        # edit_menu.addAction("Edit Filter", self.on_add_filter_button_clicked)

        view_menu = menu_bar.addMenu("&View")
        view_menu.setCursor(Qt.PointingHandCursor)
        view_menu.addAction("Open debug window", self.controller.open_debug_window)
        view_menu.addAction("Change theme", self.controller.change_theme)

        toggle_axes_action = QAction("Show/hide axes", self)
        toggle_axes_action.setCheckable(True)
        toggle_axes_action.setChecked(False)
        toggle_axes_action.toggled.connect(self.controller.show_hide_axes)
        view_menu.addAction(toggle_axes_action)

        menu_bar.addAction("&Help", self.open_help_window)
        menu_bar.setCursor(Qt.PointingHandCursor)

    def on_notify_signal(self, log: Log, message: str):
        if log != Log.DEBUG:
            self.info_label.setStyleSheet(f"color: {log.value};")
            self.info_label.setText(message)

    def closeEvent(self, event: QCloseEvent):
        self.controller.close_application()

    def change_theme(self, theme: Theme):
        if theme == Theme.DARK_MODE:
            self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        else:
            self.setStyleSheet("")

    def open_help_window(self):
        if self.help_window is None:
            self.help_window = HelpWindow()

        self.help_window.show()
        self.help_window.raise_()

    def close(self):
        if self.help_window is not None:
            self.help_window.close()

        super().close()
