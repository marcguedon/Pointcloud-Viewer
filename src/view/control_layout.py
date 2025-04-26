from sympy import Q
import yaml
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor, QColor
from view.filter_window import FilterDialog
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

        if item is None:
            raise ValueError("Item is None")

        else:
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
            parent=self.main_window,
            caption="Load pointcloud",
            directory="",
            filter="Pointcloud file (*.ply *.pcd *.xyz);;All files (*)",
        )

        if not file_path:
            self.main_window.info_label.setText("No file selected")
            self.main_window.info_label.setStyleSheet(
                "QLabel#info_label {color: black}"
            )
            return

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        if not file_path.endswith((".ply", ".pcd", ".xyz")):
            self.main_window.info_label.setText("Invalid file format")
            self.main_window.info_label.setStyleSheet("QLabel#info_label {color: red}")
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
            # return None, None, None
            raise ValueError("Row widget is None")

        checkbox = row_widget.checkbox
        label = row_widget.label
        delete_btn = row_widget.delete_btn

        return checkbox, label, delete_btn

    def on_add_filter_button_clicked(self):
        filter_name = "test" # TODO: Manage the name with the controller
        filter_bounds = (0.0, 1.0, 0.0, 1.0, 0.0, 1.0)  # Default bounds
        filter_color = QColor("black")

        filter_box = self.controller.add_filter(
            filter_name, filter_bounds, filter_color
        )
        self.main_window.show_filter(filter_name, filter_box, filter_color)

    def edit_filter(self, item):
        _, label, _, _ = self.get_filter_widgets_from_item(item)
        name = label.text

        filter = self.controller.get_filter_by_name(name)

        self.main_window.viewer_area.show_filter_dialog(filter)
        # filter_window = FilterDialog()

        # filter_bounds = filter_window.filter_bounds
        # filter_color = filter_window.filter_color

        # box = self.controller.set_filter_bounds(name, filter_bounds)
        # self.controller.set_filter_color(name, filter_color)

    def add_filter(self, item, filter_widget):
        self.filters_tree.addTopLevelItem(item)
        self.filters_tree.setItemWidget(item, 0, filter_widget)

    def remove_filter(self, item):
        self.filters_tree.takeTopLevelItem(self.filters_tree.indexOfTopLevelItem(item))

    def get_filter_widgets_from_item(self, item):
        row_widget = self.filters_tree.itemWidget(item, 0)
        
        if row_widget is None:
            raise ValueError("Row widget is None")

        checkbox = row_widget.checkbox
        label = row_widget.label
        edit_btn = row_widget.edit_btn
        delete_btn = row_widget.delete_btn

        return checkbox, label, edit_btn, delete_btn

    def filter_menu(self, position):
        item = self.filters_tree.itemAt(position)

        if item is None:
            raise ValueError("Item is None")

        else:
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

    def on_import_filter_button_clicked(self):
        file_path, _ = QFileDialog.getOpenFileName(
            parent=self.main_window,
            caption="Import filters",
            directory="",
            filters="YAML files (*.yaml *.yml);;All files (*)",
        )

        if not file_path:
            self.main_window.info_label.setText("No file selected")
            self.main_window.info_label.setStyleSheet(
                "QLabel#info_label {color: black}"
            )
            return

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        if not file_path.endswith((".yaml", ".yml")):
            self.main_window.info_label.setText("Invalid file format")
            self.main_window.info_label.setStyleSheet("QLabel#info_label {color: red}")
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

    def on_export_filter_button_clicked(self):
        filters = self.controller.get_filters()

        if not filters:
            self.main_window.info_label.setText("No filters to export")
            self.main_window.info_label.setStyleSheet(
                "QLabel#info_label {color: black}"
            )
            return

        dialog = QFileDialog(self.main_window, "Export filters")
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        dialog.setNameFilters(["YAML files (*.yaml *.yml)", "All files (*)"])
        # dialog.setDefaultSuffix("yaml") # Automatically adds .yaml extension
        dialog.setOption(QFileDialog.DontConfirmOverwrite, True)

        def correct_extension_on_click(path):
            if path and not path.endswith((".yaml", ".yml")):
                corrected = path + ".yaml"
                dialog.selectFile(corrected)

        dialog.currentChanged.connect(correct_extension_on_click)

        if dialog.exec_() == QFileDialog.Accepted:
            file_path = dialog.selectedFiles()[0]

            if os.path.exists(file_path):
                reply = QMessageBox.question(
                    self.main_window,
                    "File exists",
                    f"The file {os.path.basename(file_path)} already exists.<br>Do you want to overwrite it?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No,
                )
                if reply != QMessageBox.Yes:
                    self.main_window.info_label.setText("Export cancelled")
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
                    for filter in filters
                }
            }

            with open(file_path, "w") as file:
                yaml.dump(filters_dict, file)

            self.main_window.info_label.setText(
                f"Filters exported successfully: {os.path.basename(file_path)}"
            )
            self.main_window.info_label.setStyleSheet(
                "QLabel#info_label {color: green}"
            )
