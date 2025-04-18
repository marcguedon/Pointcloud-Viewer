import yaml
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor, QColor
from view.add_filter_window import AddFilterDialog
from view.pointcloud_menu import PointcloudMenu
from view.filter_menu import FilterMenu
from controller.controller import Controller


class ControlLayout(QVBoxLayout):
    def __init__(self, main_window=None):
        super().__init__()

        self.main_window = main_window
        self.controller = Controller()

        self.create_ui()

    def create_ui(self):
        self.setSpacing(10)

        pointcloud_layout = QVBoxLayout()
        pointcloud_layout.setSpacing(5)
        self.addLayout(pointcloud_layout)

        # Pointclouds
        load_pointcloud_btn = QPushButton("Load pointcloud")
        load_pointcloud_btn.setToolTip("Load pointcloud")
        load_pointcloud_btn.setCursor(QCursor(Qt.PointingHandCursor))
        load_pointcloud_btn.clicked.connect(self.on_load_pointcloud_button_clicked)
        pointcloud_layout.addWidget(load_pointcloud_btn)

        self.pointclouds_tree = QTreeWidget()
        self.pointclouds_tree.setHeaderLabel("Pointclouds")
        self.pointclouds_tree.setIndentation(0)
        self.pointclouds_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.pointclouds_tree.customContextMenuRequested.connect(self.pointcloud_menu)
        pointcloud_layout.addWidget(self.pointclouds_tree)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        self.addWidget(separator)

        # Filters
        filter_layout = QVBoxLayout()
        filter_layout.setSpacing(5)
        self.addLayout(filter_layout)

        add_filter_btn = QPushButton("Add Filter")
        add_filter_btn.setToolTip("Add filter")
        add_filter_btn.setCursor(QCursor(Qt.PointingHandCursor))
        add_filter_btn.clicked.connect(self.on_add_filter_button_clicked)
        filter_layout.addWidget(add_filter_btn)

        filter_file_layout = QHBoxLayout()
        filter_file_layout.setSpacing(5)
        filter_layout.addLayout(filter_file_layout)

        import_filter_btn = QPushButton("Import Filters")
        import_filter_btn.setToolTip("Import filters")
        import_filter_btn.setCursor(QCursor(Qt.PointingHandCursor))
        import_filter_btn.clicked.connect(self.on_import_filter_button_clicked)
        filter_file_layout.addWidget(import_filter_btn)

        export_filter_btn = QPushButton("Export Filters")
        export_filter_btn.setToolTip("Export filters")
        export_filter_btn.setCursor(QCursor(Qt.PointingHandCursor))
        export_filter_btn.clicked.connect(self.on_export_filter_button_clicked)
        filter_file_layout.addWidget(export_filter_btn)

        self.filters_tree = QTreeWidget()
        self.filters_tree.setHeaderLabel("Filters")
        self.filters_tree.setIndentation(0)
        self.filters_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.filters_tree.customContextMenuRequested.connect(self.filter_menu)
        filter_layout.addWidget(self.filters_tree)

        # Quit button
        quit_btn = QPushButton("Quit")
        quit_btn.setToolTip("Quit application")
        quit_btn.setCursor(QCursor(Qt.PointingHandCursor))
        quit_btn.clicked.connect(self.main_window.close)
        self.addWidget(quit_btn)

    def pointcloud_menu(self, position):
        item = self.pointclouds_tree.itemAt(position)

        if item is not None:
            menu = PointcloudMenu()

            menu.toggle_pointcloud_visibility.connect(
                lambda item=item: self.main_window.toggle_pointcloud_visibility(item)
            )
            menu.rename_pointcloud.connect(
                lambda item=item: self.main_window.trigger_pointcloud_rename(item)
            )
            menu.delete_pointcloud.connect(
                lambda item=item: self.main_window.on_remove_pointcloud_item(item)
            )

            menu.exec_(self.pointclouds_tree.viewport().mapToGlobal(position))

    def on_load_pointcloud_button_clicked(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self.main_window,
            "Load pointcloud",
            "",
            "Pointcloud file (*.ply *.pcd *.xyz)",
        )

        if not file_path:
            return

        self.main_window.add_pointcloud(file_path)

    def add_pointcloud(self, item, pointcloud_widget):
        self.pointclouds_tree.addTopLevelItem(item)
        self.pointclouds_tree.setItemWidget(item, 0, pointcloud_widget)

    def remove_pointcloud(self, item):
        self.pointclouds_tree.takeTopLevelItem(
            self.pointclouds_tree.indexOfTopLevelItem(item)
        )

    def get_pointcloud_widgets_from_item(self, item):
        row_widget = self.pointclouds_tree.itemWidget(item, 0)

        if row_widget is None:
            return None, None

        checkbox = row_widget.checkbox
        label = row_widget.label
        delete_btn = row_widget.delete_btn

        return checkbox, label, delete_btn

    def on_add_filter_button_clicked(self):
        add_filter_window = AddFilterDialog("add")
        add_filter_window.setWindowTitle("Add Filter")

        result = add_filter_window.exec_()

        if result == QDialog.Accepted:
            filter_name = add_filter_window.filter_name
            filter_bounds = add_filter_window.filter_bounds
            filter_color = add_filter_window.filter_color

            filter_box = self.controller.add_filter(
                filter_name, filter_bounds, filter_color
            )
            self.main_window.show_filter(filter_name, filter_box, filter_color)

    def edit_filter(self, item):
        _, label, _, _ = self.get_filter_widgets_from_item(item)
        name = label.text

        filter = self.controller.get_filter_by_name(name)

        add_filter_window = AddFilterDialog("edit")

        add_filter_window.name_edit.setText(name)
        add_filter_window.coord_inputs["X min"].setValue(filter.box.bounds[0])
        add_filter_window.coord_inputs["X max"].setValue(filter.box.bounds[1])
        add_filter_window.coord_inputs["Y min"].setValue(filter.box.bounds[2])
        add_filter_window.coord_inputs["Y max"].setValue(filter.box.bounds[3])
        add_filter_window.coord_inputs["Z min"].setValue(filter.box.bounds[4])
        add_filter_window.coord_inputs["Z max"].setValue(filter.box.bounds[5])
        add_filter_window.color_button.setStyleSheet(
            f"background-color: {filter.color.name()};"
        )

        result = add_filter_window.exec_()

        if result == QDialog.Accepted:
            filter_name = add_filter_window.filter_name
            filter_bounds = add_filter_window.filter_bounds
            filter_color = add_filter_window.filter_color

            label.apply_validated_text(filter_name)
            label.setToolTip(filter_name)

            self.controller.set_filter_name(name, filter_name)
            box = self.controller.set_filter_bounds(filter_name, filter_bounds)
            self.controller.set_filter_color(filter_name, filter_color)

            self.main_window.update_filter(name, filter_name, box, filter_color)

    def add_filter(self, item, filter_widget):
        self.filters_tree.addTopLevelItem(item)
        self.filters_tree.setItemWidget(item, 0, filter_widget)

    def remove_filter(self, item):
        self.filters_tree.takeTopLevelItem(self.filters_tree.indexOfTopLevelItem(item))

    def get_filter_widgets_from_item(self, item):
        row_widget = self.filters_tree.itemWidget(item, 0)
        if row_widget is None:
            return None, None

        checkbox = row_widget.checkbox
        label = row_widget.label
        edit_btn = row_widget.edit_btn
        delete_btn = row_widget.delete_btn

        return checkbox, label, edit_btn, delete_btn

    def filter_menu(self, position):
        item = self.filters_tree.itemAt(position)

        if item is not None:
            menu = FilterMenu()

            menu.toggle_filter_visibility.connect(
                lambda item=item: self.main_window.toggle_filter_visibility(item)
            )
            menu.rename_filter.connect(
                lambda item=item: self.main_window.trigger_filter_rename(item)
            )
            menu.edit_filter.connect(lambda item=item: self.edit_filter(item))
            menu.delete_filter.connect(
                lambda item=item: self.main_window.on_remove_filter_item(item)
            )

            menu.exec_(self.filters_tree.viewport().mapToGlobal(position))

    def on_export_filter_button_clicked(self):
        filters = self.controller.get_filters()

        if not filters:
            self.main_window.info_label.setText("No filters to export")
            self.main_window.info_label.setStyleSheet(
                "QLabel#info_label {color: black}"
            )
            return

        filters_dict = {
            "filters": {
                filter.name: {
                    "bounds": [round(val, 2) for val in filter.box.bounds],
                    "color": filter.color.name(),
                }
            }
            for filter in filters
        }

        file_path, _ = QFileDialog.getSaveFileName(
            self.main_window,
            "Export filters",
            "",
            "YAML files (*.yaml *.yml);;All files (*)",
        )

        if not file_path:
            return

        if not file_path.endswith((".yaml", ".yml")):
            file_path += ".yaml"

        with open(file_path, "w") as file:
            yaml.dump(filters_dict, file)

        self.main_window.info_label.setText("Filters exported successfully")
        self.main_window.info_label.setStyleSheet("QLabel#info_label {color: green}")

    def on_import_filter_button_clicked(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self.main_window,
            "Import filters",
            "",
            "YAML files (*.yaml *.yml);;All files (*)",
        )

        if not file_path:
            return

        with open(file_path, "r") as file:
            filters_dict = yaml.safe_load(file)

        for filter_name, filter_data in filters_dict["filters"].items():
            bounds = filter_data["bounds"]
            color = QColor(filter_data["color"])

            filter_box = self.controller.add_filter(filter_name, bounds, color)
            self.main_window.show_filter(filter_name, filter_box, color)

        self.main_window.info_label.setText("Filters imported successfully")
        self.main_window.info_label.setStyleSheet("QLabel#info_label {color: green}")
