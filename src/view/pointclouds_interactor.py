from pyvistaqt import QtInteractor
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMouseEvent


class PointcloudsInteractor(QtInteractor):
    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if event.button() == Qt.MiddleButton:
            self.center_on_all()
        else:
            super().mouseDoubleClickEvent(event)

    def center_on_all(self):
        bounds = self.bounds  # bounds of all visible actors
        if bounds is not None:
            self.reset_camera(bounds=bounds)
