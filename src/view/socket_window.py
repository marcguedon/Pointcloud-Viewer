from PyQt5.QtWidgets import (
    QWidget,
    QMdiSubWindow,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QStyle,
    QHBoxLayout,
    QLabel,
)
from PyQt5.QtCore import Qt, QEvent, pyqtSignal
from PyQt5.QtGui import QIntValidator, QFont
from controller.controller import Controller
from controller.socket import Socket

DEFAULT_PORT = 8080


class SocketWindow(QMdiSubWindow):
    closed = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.controller: Controller = Controller()
        self.socket = Socket()

        self.is_collapsed: bool = False
        self.title_bar_height = self.style().pixelMetric(QStyle.PM_TitleBarHeight)

        self.setWindowTitle("Socket")
        self.setWindowFlags(
            Qt.WindowCloseButtonHint
            | Qt.WindowMinimizeButtonHint
            | Qt.WindowStaysOnTopHint
            | Qt.MSWindowsFixedSizeDialogHint
        )
        self.setAttribute(Qt.WA_DeleteOnClose, True)

        self.normal_size: bool = None
        self.create_ui()

    def create_ui(self):
        main_widget = QWidget()
        self.setWidget(main_widget)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(8)
        main_widget.setLayout(main_layout)

        port_layout = QHBoxLayout()
        port_layout.setContentsMargins(0, 5, 0, 0)
        port_layout.setSpacing(5)

        port_label = QLabel("Port:")
        port_label.setFont(QFont("Arial", 10))
        port_layout.addWidget(port_label)

        self.port_edit = QLineEdit()
        self.port_edit.setFont(QFont("Arial", 10))
        self.port_edit.setToolTip("Enter port number")
        validator = QIntValidator(0, 65535)
        self.port_edit.setValidator(validator)
        self.port_edit.setPlaceholderText(f"Default: {DEFAULT_PORT}")
        port_layout.addWidget(self.port_edit)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(5)

        self.stop_button = QPushButton("Stop")
        self.stop_button.setFont(QFont("Arial", 10))
        self.stop_button.setEnabled(False)
        self.stop_button.setToolTip("Stop socket server")
        self.stop_button.clicked.connect(self.on_stop_socket_button)
        button_layout.addWidget(self.stop_button)

        self.start_button = QPushButton("Start")
        self.start_button.setFont(QFont("Arial", 10))
        self.start_button.setToolTip("Start socket server")
        self.start_button.clicked.connect(self.on_start_socket_button)
        button_layout.addWidget(self.start_button)

        main_layout.addLayout(port_layout)
        main_layout.addLayout(button_layout)

        self.normal_height = self.sizeHint().height()

        if self.socket.is_running:
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.port_edit.setEnabled(False)
            self.port_edit.setText(str(self.socket.port))

    def closeEvent(self, event):
        self.closed.emit()
        super().closeEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.handle_minimize()

        event.accept()

    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange:
            if self.windowState():
                self.handle_minimize()

        event.accept()

    def handle_minimize(self):
        self.is_collapsed = not self.is_collapsed
        self.showNormal()

        if self.is_collapsed:
            self.setWindowFlags(
                Qt.WindowCloseButtonHint
                | Qt.WindowMaximizeButtonHint
                | Qt.WindowStaysOnTopHint
                | Qt.MSWindowsFixedSizeDialogHint
            )
            self.setFixedHeight(self.title_bar_height)
        else:
            self.setWindowFlags(
                Qt.WindowCloseButtonHint
                | Qt.WindowMinimizeButtonHint
                | Qt.WindowStaysOnTopHint
                | Qt.MSWindowsFixedSizeDialogHint
            )
            self.setFixedHeight(self.normal_height + self.title_bar_height)

    def on_start_socket_button(self):
        port = self.port_edit.text()

        if not port:
            port = DEFAULT_PORT

        else:
            port = int(port)

        self.port_edit.setText(str(port))
        self.port_edit.setEnabled(False)
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

        self.controller.start_socket(port)

    def on_stop_socket_button(self):
        self.port_edit.setEnabled(True)
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

        self.controller.stop_socket()
