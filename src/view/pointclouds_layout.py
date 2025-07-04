from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QTreeWidget, QTreeWidgetItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from controller.controller import Controller
from view.pointcloud_widget import PointcloudWidget
from view.droppable_tree_widget import DroppableTreeWidget
from model.pointcloud import Pointcloud


class PointcloudsLayout(QVBoxLayout):
    def __init__(self):
        super().__init__()

        self.controller: Controller = Controller()
        self.controller.add_pointcloud_signal.connect(self.add_pointcloud)
        self.controller.delete_pointcloud_signal.connect(self.remove_pointcloud_item)

        self.create_ui()

    def create_ui(self):
        self.setSpacing(5)

        load_pointcloud_btn = QPushButton("Load pointcloud")
        load_pointcloud_btn.setToolTip("Load pointcloud")
        load_pointcloud_btn.setCursor(QCursor(Qt.PointingHandCursor))
        load_pointcloud_btn.clicked.connect(self.controller.load_pointcloud_files)
        self.addWidget(load_pointcloud_btn)

        self.pointclouds_tree = DroppableTreeWidget(self.controller.load_pointcloud)
        self.pointclouds_tree.setHeaderLabel("Pointclouds")
        self.pointclouds_tree.setIndentation(0)
        self.pointclouds_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.addWidget(self.pointclouds_tree)

    def add_pointcloud(self, pointcloud: Pointcloud):
        item = QTreeWidgetItem(self.pointclouds_tree)
        pointcloud_widget = PointcloudWidget(pointcloud)

        self.add_pointcloud_item(item, pointcloud_widget)

    def add_pointcloud_item(
        self, item: QTreeWidgetItem, pointcloud_widget: PointcloudWidget
    ):
        self.pointclouds_tree.addTopLevelItem(item)
        self.pointclouds_tree.setItemWidget(item, 0, pointcloud_widget)

    def remove_pointcloud_item(self, pointcloud: Pointcloud):
        for i in range(self.pointclouds_tree.topLevelItemCount()):
            item = self.pointclouds_tree.topLevelItem(i)
            pointcloud_widget = self.pointclouds_tree.itemWidget(item, 0)

            if pointcloud_widget.pointcloud == pointcloud:
                self.pointclouds_tree.takeTopLevelItem(i)
                break
