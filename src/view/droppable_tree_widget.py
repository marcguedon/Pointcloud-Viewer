from PyQt5.QtWidgets import QTreeWidget
from PyQt5.QtGui import QDragEnterEvent, QDragMoveEvent, QDropEvent


class DroppableTreeWidget(QTreeWidget):
    def __init__(self, function):
        super().__init__()

        self.function = function

        self.setAcceptDrops(True)

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
                self.function(file_path)

            event.acceptProposedAction()

        else:
            event.ignore()
