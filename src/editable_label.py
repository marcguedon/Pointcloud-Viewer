from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QVBoxLayout
from PyQt5.QtCore import pyqtSignal


class EditableLabel(QWidget):
    text_changed = pyqtSignal(str)

    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self.label = QLabel(text)
        self.line_edit = QLineEdit(text)
        self.line_edit.hide()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.label)
        layout.addWidget(self.line_edit)

        self.label.mouseDoubleClickEvent = self.enter_edit_mode
        self.line_edit.editingFinished.connect(self.leave_edit_mode)

    def toolTip(self):
        return super().toolTip()

    def enter_edit_mode(self, event):
        self.label.hide()
        self.line_edit.setText(self.label.text())
        self.line_edit.show()
        self.line_edit.setFocus()
        self.line_edit.selectAll()

    def leave_edit_mode(self):
        new_text = self.line_edit.text()
        self.text_changed.emit(new_text)

    def text(self):
        return self.label.text()

    def setText(self, text):
        self.label.setText(text)
        self.line_edit.setText(text)
