from PyQt5.QtWidgets import (
    QWidget,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QMenuBar,
    QAction,
)
from controller.controller import Controller
from view.control_layout import ControlLayout
from view.viewer_area import ViewerArea
from utils.log import Log


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.controller: Controller = Controller()
        self.controller.notify_signal.connect(self.on_notify_signal)
        self.controller.close_application_signal.connect(self.close)

        self.setWindowTitle("Pointclouds Viewer")
        self.resize(1920, 1080)

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

        self.info_label = QLabel("")
        self.info_label.setObjectName("info_label")
        main_layout.addWidget(self.info_label)

        self.create_menu()

    def create_menu(self):
        menu_bar = QMenuBar()
        self.setMenuBar(menu_bar)

        file_menu = menu_bar.addMenu("&Data")
        file_menu.addAction("Load pointcloud", self.controller.load_pointcloud)
        file_menu.addAction("Open socket window", self.controller.open_socket_window)
        file_menu.addSeparator()
        file_menu.addAction("Add Filter", self.controller.add_filter)
        file_menu.addSeparator()
        file_menu.addAction("Quit", self.controller.close_application)

        # edit_menu = menu_bar.addMenu("&Edit")
        # edit_menu.addAction("Add Filter", self.on_add_filter_button_clicked)
        # edit_menu.addAction("Remove Filter", self.on_add_filter_button_clicked)
        # edit_menu.addAction("Edit Filter", self.on_add_filter_button_clicked)

        view_menu = menu_bar.addMenu("&View")
        view_menu.addAction("Change theme", self.controller.change_theme)

        toggle_axes_action = QAction("Show/hide axes", self)
        toggle_axes_action.setCheckable(True)
        toggle_axes_action.setChecked(False)
        toggle_axes_action.toggled.connect(self.controller.show_hide_axes)
        view_menu.addAction(toggle_axes_action)

    def on_notify_signal(self, log: Log, message: str):
        if log == Log.SUCCESS:
            self.info_label.setStyleSheet("color: green;")
        elif log == Log.INFO:
            self.info_label.setStyleSheet("color: black;")
        elif log == Log.WARNING:
            self.info_label.setStyleSheet("color: orange;")
        elif log == Log.ERROR:
            self.info_label.setStyleSheet("color: red;")

        self.info_label.setText(message)
