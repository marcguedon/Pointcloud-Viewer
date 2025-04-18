from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QVBoxLayout
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFontMetrics


class EditableLabel(QWidget):
    text_confirmed = pyqtSignal(str)

    def __init__(self, text="", parent=None):
        super().__init__(parent)

        self._full_text = text

        self.label = QLabel()
        self.line_edit = QLineEdit()
        self.line_edit.hide()
        self.set_text()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.label)
        layout.addWidget(self.line_edit)

        self.label.mouseDoubleClickEvent = self.enter_edit_mode
        self.line_edit.returnPressed.connect(self.confirm_edit)
        self.line_edit.editingFinished.connect(self.cancel_edit_if_needed)

        self._in_confirm = False

    def enter_edit_mode(self, event=None):
        self.label.hide()
        self.line_edit.setText(self._full_text)
        self.line_edit.show()
        self.line_edit.setFocus()
        self.line_edit.selectAll()

    def confirm_edit(self):
        self._in_confirm = True
        new_text = self.line_edit.text()
        self.text_confirmed.emit(new_text)

    def cancel_edit_if_needed(self):
        if not self._in_confirm:
            self.cancel_edit()

        self._in_confirm = False

    def cancel_edit(self):
        self.line_edit.hide()
        self.label.show()

    def apply_validated_text(self, text):
        self._full_text = text
        self.set_text()
        self.label.show()
        self.line_edit.hide()

    @property
    def text(self):
        return self._full_text

    def set_text(self):
        metrics = QFontMetrics(self.label.font())
        elided = metrics.elidedText(self._full_text, Qt.ElideRight, self.label.width())
        self.label.setText(elided)
        self.line_edit.setText(elided)
