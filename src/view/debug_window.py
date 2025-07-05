from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget,
    QMdiSubWindow,
    QVBoxLayout,
    QHBoxLayout,
    QStyle,
    QTextEdit,
    QCheckBox,
    QLabel,
    QToolButton,
    QPushButton,
    QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QEvent, pyqtSignal
from PyQt5.QtGui import QCursor, QColor
from controller.controller import Controller
from utils.log import Log

DEFAULT_PORT = 8080


class DebugWindow(QMdiSubWindow):
    closed = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.controller: Controller = Controller()
        self.controller.notify_signal.connect(self.show_log)

        self.is_autoscroll_on = False
        self.show_timestamp = False

        self.is_collapsed: bool = False
        self.title_bar_height = self.style().pixelMetric(QStyle.PM_TitleBarHeight)

        self.setWindowTitle("Debug")
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

        # TODO: Improve the control_layout display
        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(0, 5, 0, 0)
        control_layout.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        main_layout.addLayout(control_layout)

        self.toggle_autoscroll_button = QPushButton("⇟")
        self.toggle_autoscroll_button.setFixedSize(20, 20)
        self.toggle_autoscroll_button.setToolTip("Toggle autoscroll")
        self.toggle_autoscroll_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.toggle_autoscroll_button.clicked.connect(
            lambda state: self.on_toggle_autoscroll_button()
        )
        control_layout.addWidget(self.toggle_autoscroll_button)

        self.toggle_timestamp_button = QPushButton("⧖")
        self.toggle_timestamp_button.setFixedSize(20, 20)
        self.toggle_timestamp_button.setToolTip("Toggle timestamp")
        self.toggle_timestamp_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.toggle_timestamp_button.clicked.connect(
            lambda state: self.on_toggle_timestamp_button()
        )
        control_layout.addWidget(self.toggle_timestamp_button)

        self.clear_button = QPushButton("Clear")
        self.clear_button.setFixedSize(50, 20)
        self.clear_button.setToolTip("Clear debug window")
        self.clear_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.clear_button.clicked.connect(self.on_clear_button)
        control_layout.addWidget(self.clear_button)

        self.debug_text_edit = QTextEdit()
        self.debug_text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        main_layout.addWidget(self.debug_text_edit)

        log_level_layout = QHBoxLayout()
        log_level_layout.setAlignment(Qt.AlignVCenter)
        main_layout.addLayout(log_level_layout)

        error_level_layout = QHBoxLayout()
        error_level_layout.setSpacing(5)
        log_level_layout.addLayout(error_level_layout)

        error_level_label = QLabel("ERROR:")
        error_level_layout.addWidget(error_level_label)

        self.error_level_checkbox = QCheckBox()
        self.error_level_checkbox.setToolTip("Show/hide error level logs")
        self.error_level_checkbox.setCursor(QCursor(Qt.PointingHandCursor))
        self.error_level_checkbox.setChecked(True)
        error_level_layout.addWidget(self.error_level_checkbox)

        warning_level_layout = QHBoxLayout()
        warning_level_layout.setSpacing(5)
        log_level_layout.addLayout(warning_level_layout)

        warning_level_label = QLabel("WARNING:")
        warning_level_layout.addWidget(warning_level_label)

        self.warning_level_checkbox = QCheckBox()
        self.warning_level_checkbox.setToolTip("Show/hide warning level logs")
        self.warning_level_checkbox.setCursor(QCursor(Qt.PointingHandCursor))
        self.warning_level_checkbox.setChecked(True)
        warning_level_layout.addWidget(self.warning_level_checkbox)

        info_level_layout = QHBoxLayout()
        info_level_layout.setSpacing(5)
        log_level_layout.addLayout(info_level_layout)

        info_level_label = QLabel("INFO:")
        info_level_layout.addWidget(info_level_label)

        self.info_level_checkbox = QCheckBox()
        self.info_level_checkbox.setToolTip("Show/hide info level logs")
        self.info_level_checkbox.setCursor(QCursor(Qt.PointingHandCursor))
        self.info_level_checkbox.setChecked(True)
        info_level_layout.addWidget(self.info_level_checkbox)

        success_level_layout = QHBoxLayout()
        success_level_layout.setSpacing(5)
        log_level_layout.addLayout(success_level_layout)

        success_level_label = QLabel("SUCCESS:")
        success_level_layout.addWidget(success_level_label)

        self.success_level_checkbox = QCheckBox()
        self.success_level_checkbox.setToolTip("Show/hide success level logs")
        self.success_level_checkbox.setCursor(QCursor(Qt.PointingHandCursor))
        self.success_level_checkbox.setChecked(True)
        success_level_layout.addWidget(self.success_level_checkbox)

        debug_level_layout = QHBoxLayout()
        debug_level_layout.setSpacing(5)
        log_level_layout.addLayout(debug_level_layout)

        debug_level_label = QLabel("DEBUG:")
        debug_level_layout.addWidget(debug_level_label)

        self.debug_level_checkbox = QCheckBox()
        self.debug_level_checkbox.setToolTip("Show/hide debug level logs")
        self.debug_level_checkbox.setCursor(QCursor(Qt.PointingHandCursor))
        self.debug_level_checkbox.setChecked(True)
        debug_level_layout.addWidget(self.debug_level_checkbox)

        self.normal_height = self.sizeHint().height()

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

    def on_clear_button(self):
        self.debug_text_edit.clear()

    def on_toggle_autoscroll_button(self):
        self.is_autoscroll_on = not self.is_autoscroll_on

        if self.is_autoscroll_on:
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(15)
            shadow.setOffset(0, 0)
            shadow.setColor(QColor(0, 191, 255))
            self.toggle_autoscroll_button.setGraphicsEffect(shadow)
            
            scroll_bar = self.debug_text_edit.verticalScrollBar()
            scroll_bar.setValue(scroll_bar.maximum())
            
        else:
            self.toggle_autoscroll_button.setGraphicsEffect(None)

    def on_toggle_timestamp_button(self):
        self.show_timestamp = not self.show_timestamp
        self.controller.notify(
            Log.DEBUG, "Show timestamp" if self.show_timestamp else "Hide timestamp"
        )
        
        if self.show_timestamp:
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(15)
            shadow.setOffset(0, 0)
            shadow.setColor(QColor(0, 191, 255))
            self.toggle_timestamp_button.setGraphicsEffect(shadow)
            
        else:
            self.toggle_timestamp_button.setGraphicsEffect(None)

    def show_log(self, log: Log, message: str):
        should_display = {
            Log.DEBUG: self.debug_level_checkbox.isChecked(),
            Log.SUCCESS: self.success_level_checkbox.isChecked(),
            Log.INFO: self.info_level_checkbox.isChecked(),
            Log.WARNING: self.warning_level_checkbox.isChecked(),
            Log.ERROR: self.error_level_checkbox.isChecked(),
        }

        if should_display.get(log, False):
            scroll_bar = self.debug_text_edit.verticalScrollBar()
            previous_scroll_value = scroll_bar.value()

            if self.show_timestamp:
                timestamp = datetime.now().strftime("%H:%M:%S")
                log_text = f'<span style="color:{log.value};">[{timestamp}][{str(log)}]: {message}</span>'

            else:
                log_text = (
                    f'<span style="color:{log.value};">[{str(log)}]: {message}</span>'
                )

            self.debug_text_edit.append(log_text)

            if self.is_autoscroll_on:
                scroll_bar.setValue(scroll_bar.maximum())
            else:
                scroll_bar.setValue(previous_scroll_value)
