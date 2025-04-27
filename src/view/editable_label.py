from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QVBoxLayout
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFontMetrics


class EditableLabel(QWidget):
    confirm_text = pyqtSignal(str)

    def __init__(self, text: str = ""):
        super().__init__()

        self._full_text = text

        self.label = QLabel(self._full_text)
        self.line_edit = QLineEdit()
        self.line_edit.hide()
        self.set_text()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.label)
        layout.addWidget(self.line_edit)

        self.label.mouseDoubleClickEvent = self.enter_edit_mode
        self.line_edit.returnPressed.connect(self.emit_changed_text)
        self.line_edit.editingFinished.connect(self.cancel_edit)

    def enter_edit_mode(self, event=None):
        self.label.hide()
        self.line_edit.setText(self._full_text)
        self.line_edit.show()
        self.line_edit.setFocus()
        self.line_edit.selectAll()

    def cancel_edit(self):
        self.line_edit.hide()
        self.label.show()

    def apply_validated_text(self):
        self._full_text = self.line_edit.text()
        self.set_text()
        self.label.show()
        self.line_edit.hide()

    def emit_changed_text(self):
        self.confirm_text.emit(self.line_edit.text())

    @property
    def text(self):
        return self._full_text

    def set_text(self):
        metrics = QFontMetrics(self.label.font())
        elided = metrics.elidedText(self._full_text, Qt.ElideRight, self.label.width())
        self.label.setText(elided)
        self.line_edit.setText(elided)
