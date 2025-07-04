from pyvistaqt import QtInteractor
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMouseEvent, QDragEnterEvent, QDragMoveEvent, QDropEvent


class PointcloudsInteractor(QtInteractor):
    def __init__(self, pointcloud_function, filters_function):
        super().__init__()

        self.pointcloud_function = pointcloud_function
        self.filters_function = filters_function

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if event.button() == Qt.MiddleButton:
            self.center_on_all()
        # else:
        #     super().mouseDoubleClickEvent(event)

    def center_on_all(self):
        bounds = self.bounds  # bounds of all visible actors
        if bounds is not None:
            self.reset_camera(bounds=bounds)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

        else:
            event.ignore()

    def dragMoveEvent(self, event: QDragMoveEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()

                # Pointcloud file
                if file_path.lower().endswith((".ply", ".pcd", ".xyz", ".npy", ".npz")):
                    self.pointcloud_function(file_path)

                # Filters file
                elif file_path.lower().endswith((".yaml", ".yml")):
                    self.filters_function(file_path)

            event.acceptProposedAction()

        else:
            event.ignore()
