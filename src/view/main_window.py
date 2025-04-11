from re import L
import pyvista as pv
from pyvistaqt import QtInteractor
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from editable_label import EditableLabel


class MainWindow(QMainWindow):
    def __init__(self, controller, parent=None):
        super().__init__(parent)

        self.controller = controller

        self.setWindowTitle("Pointclouds Viewer")
        self.resize(1920, 1080)

        self.theme = "white"

        self.plotter_actors = {}

        self.create_ui()

    def create_ui(self):
        self.create_menu()

        window_widget = QWidget()
        self.setCentralWidget(window_widget)

        main_layout = QVBoxLayout()
        window_widget.setLayout(main_layout)

        sub_main_layout = QHBoxLayout()
        main_layout.addLayout(sub_main_layout)

        self.info_label = QLabel("")
        self.info_label.setObjectName("info_label")
        main_layout.addWidget(self.info_label)

        control_panel = self.create_control_panel()
        sub_main_layout.addLayout(control_panel)

        viewer_panel = QVBoxLayout()
        sub_main_layout.addLayout(viewer_panel, stretch=4)

        self.plotter = QtInteractor()
        self.plotter.set_background("white")
        viewer_panel.addWidget(self.plotter.interactor)

    def create_menu(self):
        menu_bar = QMenuBar()
        self.setMenuBar(menu_bar)

        file_menu = menu_bar.addMenu("&File")
        file_menu.addAction("Load pointcloud", self.on_load_pointcloud_button_clicked)
        file_menu.addSeparator()
        file_menu.addAction("Quit", self.close)

        # edit_menu = menu_bar.addMenu("&Edit")
        # edit_menu.addAction("Add Filter", self.on_add_filter_button_clicked)
        # edit_menu.addAction("Remove Filter", self.on_add_filter_button_clicked)
        # edit_menu.addAction("Edit Filter", self.on_add_filter_button_clicked)

        view_menu = menu_bar.addMenu("&View")
        view_menu.addAction("Change theme", self.on_change_theme)

    def create_control_panel(self):
        control_panel = QVBoxLayout()

        pointcloud_layout = QVBoxLayout()
        control_panel.addLayout(pointcloud_layout)

        load_pointcloud_btn = QPushButton("Load pointcloud")
        load_pointcloud_btn.setToolTip("Load pointcloud")
        load_pointcloud_btn.setCursor(QCursor(Qt.PointingHandCursor))
        load_pointcloud_btn.clicked.connect(self.on_load_pointcloud_button_clicked)
        pointcloud_layout.addWidget(load_pointcloud_btn)

        self.pointclouds_tree = QTreeWidget()
        self.pointclouds_tree.setHeaderLabel("Pointclouds")
        self.pointclouds_tree.setIndentation(0)
        self.pointclouds_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.pointclouds_tree.customContextMenuRequested.connect(
            self.show_pointclouds_menu
        )
        pointcloud_layout.addWidget(self.pointclouds_tree)

        # filter_layout = QVBoxLayout()
        # control_panel.addLayout(filter_layout)

        # add_filter_btn = QPushButton("Add Filter")
        # add_filter_btn.setToolTip("Add filter")
        # add_filter_btn.setCursor(QCursor(Qt.PointingHandCursor))
        # add_filter_btn.clicked.connect(self.on_add_filter_button_clicked)
        # filter_layout.addWidget(add_filter_btn)

        # self.filters_tree = QTreeWidget()
        # self.filters_tree.setHeaderLabel("Filters")
        # filter_layout.addWidget(self.filters_tree)

        quit_btn = QPushButton("Quit")
        quit_btn.setToolTip("Quit application")
        quit_btn.setCursor(QCursor(Qt.PointingHandCursor))
        quit_btn.clicked.connect(self.close)
        control_panel.addWidget(quit_btn)

        return control_panel

    def on_change_theme(self):
        if self.theme == "white":
            self.plotter.set_background("black")
            self.theme = "black"
        else:
            self.plotter.set_background("white")
            self.theme = "white"

    def get_pointcloud_widgets_from_item(self, item):
        row_widget = self.pointclouds_tree.itemWidget(item, 0)
        if row_widget is None:
            return None, None

        checkbox = row_widget.findChild(QCheckBox, "pcd_visibility_checkbox")
        label = row_widget.findChild(EditableLabel, "pcd_name_label")
        delete_btn = row_widget.findChild(QPushButton, "pcd_delete_btn")

        return checkbox, label, delete_btn

    def on_load_pointcloud_button_clicked(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load pointcloud",
            "",
            "Pointcloud file (*.ply *.pcd *.xyz)",
        )

        if not file_path:
            return

        name, pointcloud_data = self.controller.load_pointcloud(file_path)

        self.show_pointcloud(name, pointcloud_data)

    # def on_add_filter_button_clicked(self):
    #     print("Ajouter un filtre")

    def show_pointclouds_menu(self, position):
        item = self.pointclouds_tree.itemAt(position)

        if item is not None:
            menu = QMenu(self)

            visibility_action = QAction("Toggle visibility", self)
            visibility_action.triggered.connect(
                lambda: self.toggle_pointcloud_visibility(item)
            )
            menu.addAction(visibility_action)

            rename_action = QAction("Rename", self)
            rename_action.triggered.connect(
                lambda: self.trigger_pointcloud_rename(item)
            )
            menu.addAction(rename_action)

            delete_action = QAction("Delete", self)
            delete_action.triggered.connect(
                lambda: self.on_remove_pointcloud_item(item)
            )
            menu.addAction(delete_action)

            menu.exec_(self.pointclouds_tree.viewport().mapToGlobal(position))

    def show_pointcloud(self, name, pointcloud_data):
        item = QTreeWidgetItem()
        self.pointclouds_tree.addTopLevelItem(item)

        row_widget = QWidget()

        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignVCenter)
        row_widget.setLayout(layout)

        sub_layout = QHBoxLayout()
        sub_layout.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        layout.addLayout(sub_layout)

        checkbox = QCheckBox()
        checkbox.setToolTip("Show/Hide pointcloud")
        checkbox.setObjectName("pcd_visibility_checkbox")
        checkbox.setChecked(True)
        checkbox.setCursor(QCursor(Qt.PointingHandCursor))
        checkbox.stateChanged.connect(
            lambda state, item=item: self.on_toggle_pointcloud_visibility(item)
        )
        sub_layout.addWidget(checkbox)

        label = EditableLabel(name)
        label.setMinimumWidth(180)
        label.text_confirmed.connect(
            lambda text, item=item: self.change_pointcloud_name(item, text)
        )
        label.setObjectName("pcd_name_label")
        label.setCursor(QCursor(Qt.PointingHandCursor))
        label.setToolTip(name)
        sub_layout.addWidget(label)

        delete_btn = QPushButton("X")
        delete_btn.setToolTip("Delete pointcloud")
        delete_btn.setObjectName("pcd_delete_btn")
        delete_btn.setFixedSize(20, 20)
        delete_btn.setCursor(QCursor(Qt.PointingHandCursor))
        delete_btn.clicked.connect(
            lambda state, item=item: self.on_remove_pointcloud_item(item)
        )
        layout.addWidget(delete_btn)

        self.pointclouds_tree.setItemWidget(item, 0, row_widget)

        actor = self.plotter.add_mesh(pointcloud_data, show_scalar_bar=False)
        self.plotter_actors[name] = actor

        self.info_label.setText(
            f"Pointcloud loaded: {name} ({pointcloud_data.n_points} points)"
        )
        self.info_label.setStyleSheet("QLabel#info_label {color: green}")

    def on_toggle_pointcloud_visibility(self, item):
        checkbox, label, _ = self.get_pointcloud_widgets_from_item(item)
        name = label.toolTip()

        if checkbox.isChecked():
            pointcloud_data = self.controller.get_pointcloud_by_name(name).points
            actor = self.plotter.add_mesh(pointcloud_data, show_scalar_bar=False)
            self.plotter_actors[name] = actor
            self.info_label.setText(f"Toggle pointcloud visibility: shown ({name})")
        else:
            self.plotter.remove_actor(self.plotter_actors[name])
            self.plotter_actors.pop(name)
            self.info_label.setText(f"Toggle pointcloud visibility: hidden ({name})")

        self.info_label.setStyleSheet("QLabel#info_label {color: black}")

    def toggle_pointcloud_visibility(self, item):
        checkbox, _, _ = self.get_pointcloud_widgets_from_item(item)

        checkbox.setChecked(not checkbox.isChecked())

    def change_pointcloud_name(self, item, new_name=None):
        _, label, _ = self.get_pointcloud_widgets_from_item(item)
        name = label.text()

        if new_name and new_name != name:
            is_available = self.controller.is_pointcloud_name_available(new_name)

            if is_available:
                self.plotter_actors[new_name] = self.plotter_actors.pop(name)
                self.plotter_actors[new_name].name = new_name
                self.controller.rename_pointcloud(name, new_name)
                label.apply_validated_text(new_name)
                label.setToolTip(new_name)

                self.info_label.setText(f"Pointcloud renamed: {name} -> {new_name}")
                self.info_label.setStyleSheet("QLabel#info_label {color: green}")

            else:
                label.cancel_edit()
            
                self.info_label.setText(f"Pointcloud name already exists: {new_name}")
                self.info_label.setStyleSheet("QLabel#info_label {color: red}")

        else:
            label.cancel_edit()

            self.info_label.setText("Pointcloud name unchanged")
            self.info_label.setStyleSheet("QLabel#info_label {color: black}")

    def trigger_pointcloud_rename(self, item):
        _, label, _ = self.get_pointcloud_widgets_from_item(item)

        if isinstance(label, EditableLabel):
            label.enter_edit_mode(None)

    def on_remove_pointcloud_item(self, item):
        _, label, _ = self.get_pointcloud_widgets_from_item(item)
        name = label.toolTip()

        self.pointclouds_tree.takeTopLevelItem(
            self.pointclouds_tree.indexOfTopLevelItem(item)
        )

        self.plotter.remove_actor(self.plotter_actors[name])
        self.plotter_actors.pop(name)

        self.controller.delete_pointcloud(name)
        self.info_label.setText(f"Pointcloud removed: {name}")
        self.info_label.setStyleSheet("QLabel#info_label {color: green}")

    # def on_add_filter_button_clicked(self):
    #     print("Ajouter un filtre")
