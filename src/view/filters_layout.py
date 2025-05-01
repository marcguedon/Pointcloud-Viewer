from PyQt5.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from controller.controller import Controller
from view.filter_widget import FilterWidget
from model.filter import Filter


class FiltersLayout(QVBoxLayout):
    def __init__(self):
        super().__init__()

        self.controller: Controller = Controller()
        self.controller.add_filter_signal.connect(self.add_filter)
        self.controller.delete_filter_signal.connect(self.remove_filter_item)

        self.create_ui()

    def create_ui(self):
        self.setSpacing(5)

        add_filter_btn = QPushButton("Add Filter")
        add_filter_btn.setToolTip("Add filter")
        add_filter_btn.setCursor(QCursor(Qt.PointingHandCursor))
        add_filter_btn.clicked.connect(self.on_add_filter_button_clicked)
        self.addWidget(add_filter_btn)

        filter_file_layout = QHBoxLayout()
        filter_file_layout.setSpacing(5)
        self.addLayout(filter_file_layout)

        import_filter_btn = QPushButton("Import Filters")
        import_filter_btn.setToolTip("Import filters")
        import_filter_btn.setCursor(QCursor(Qt.PointingHandCursor))
        import_filter_btn.clicked.connect(self.controller.import_filter)
        filter_file_layout.addWidget(import_filter_btn)

        export_filter_btn = QPushButton("Export Filters")
        export_filter_btn.setToolTip("Export filters")
        export_filter_btn.setCursor(QCursor(Qt.PointingHandCursor))
        export_filter_btn.clicked.connect(self.controller.export_filter)
        filter_file_layout.addWidget(export_filter_btn)

        self.filters_tree = QTreeWidget()
        self.filters_tree.setHeaderLabel("Filters")
        self.filters_tree.setIndentation(0)
        self.filters_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.addWidget(self.filters_tree)

    def on_add_filter_button_clicked(self):
        # Default filters values
        filter_name = "filter"
        filter_bounds = (0.0, 1.0, 0.0, 1.0, 0.0, 1.0)
        filter_color = "black"

        self.controller.add_filter(filter_name, filter_bounds, filter_color)

    def add_filter(self, filter: Filter):
        item = QTreeWidgetItem(self.filters_tree)
        filter_widget = FilterWidget(filter)

        self.add_filter_item(item, filter_widget)

    def add_filter_item(self, item: QTreeWidgetItem, filter_widget: FilterWidget):
        self.filters_tree.addTopLevelItem(item)
        self.filters_tree.setItemWidget(item, 0, filter_widget)

    def remove_filter_item(self, filter: Filter):
        for i in range(self.filters_tree.topLevelItemCount()):
            item = self.filters_tree.topLevelItem(i)
            filter_widget = self.filters_tree.itemWidget(item, 0)

            if filter_widget.filter == filter:
                self.filters_tree.takeTopLevelItem(i)
                break
