from PyQt5.QtWidgets import *
from view import viewer_layout
from view.editable_label import EditableLabel
from view.control_layout import ControlLayout
from view.viewer_layout import ViewerLayout
from view.pointcloud_widget import PointcloudWidget
from view.filter_widget import FilterWidget
from controller.controller import Controller


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.controller = Controller()

        self.setWindowTitle("Pointclouds Viewer")
        self.resize(1920, 1080)

        self.create_ui()

    def create_ui(self):
        window_widget = QWidget()
        self.setCentralWidget(window_widget)

        main_layout = QVBoxLayout()
        window_widget.setLayout(main_layout)

        sub_main_layout = QHBoxLayout()
        main_layout.addLayout(sub_main_layout)

        self.info_label = QLabel("")
        self.info_label.setObjectName("info_label")
        main_layout.addWidget(self.info_label)

        self.control_layout = ControlLayout(self)
        sub_main_layout.addLayout(self.control_layout)

        self.viewer_layout = ViewerLayout()
        sub_main_layout.addLayout(self.viewer_layout, stretch=4)

        self.create_menu()

    def create_menu(self):
        menu_bar = QMenuBar()
        self.setMenuBar(menu_bar)

        file_menu = menu_bar.addMenu("&File")
        file_menu.addAction(
            "Load pointcloud", self.control_layout.on_load_pointcloud_button_clicked
        )
        file_menu.addSeparator()
        file_menu.addAction("Quit", self.close)

        # edit_menu = menu_bar.addMenu("&Edit")
        # edit_menu.addAction("Add Filter", self.on_add_filter_button_clicked)
        # edit_menu.addAction("Remove Filter", self.on_add_filter_button_clicked)
        # edit_menu.addAction("Edit Filter", self.on_add_filter_button_clicked)

        view_menu = menu_bar.addMenu("&View")
        view_menu.addAction("Change theme", self.viewer_layout.change_theme)

    def add_pointcloud(self, name):
        name, pointcloud_data = self.controller.load_pointcloud(name)

        item = QTreeWidgetItem()

        pointcloud_widget = PointcloudWidget(name)
        pointcloud_widget.visibility_changed.connect(
            lambda visible: self.on_toggle_pointcloud_visibility(item)
        )
        pointcloud_widget.name_changed.connect(
            lambda new_name: self.change_pointcloud_name(item, new_name)
        )
        pointcloud_widget.delete_requested.connect(
            lambda: self.on_remove_pointcloud_item(item)
        )

        self.control_layout.add_pointcloud(item, pointcloud_widget)

        self.viewer_layout.display_pointcloud(name, pointcloud_data)

        self.info_label.setText(
            f"Pointcloud loaded: {name} ({pointcloud_data.n_points} points)"
        )
        self.info_label.setStyleSheet("QLabel#info_label {color: green}")

    def on_toggle_pointcloud_visibility(self, item):
        checkbox, label, _ = self.control_layout.get_pointcloud_widgets_from_item(item)
        name = label.toolTip()

        if checkbox.isChecked():
            pointcloud_data = self.controller.get_pointcloud_by_name(name).points
            self.viewer_layout.display_pointcloud(name, pointcloud_data)
            self.info_label.setText(f"Toggle pointcloud visibility: shown ({name})")
        else:
            self.viewer_layout.hide_pointcloud(name)
            self.info_label.setText(f"Toggle pointcloud visibility: hidden ({name})")

        self.info_label.setStyleSheet("QLabel#info_label {color: black}")

    def toggle_pointcloud_visibility(self, item):
        checkbox, _, _ = self.control_layout.get_pointcloud_widgets_from_item(item)

        checkbox.setChecked(not checkbox.isChecked())

    def change_pointcloud_name(self, item, new_name=None):
        _, label, _ = self.control_layout.get_pointcloud_widgets_from_item(item)
        name = label.text

        if new_name and new_name != name:
            is_available = self.controller.is_pointcloud_name_available(new_name)

            if is_available:
                self.viewer_layout.change_actor_name(name, new_name)
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
        _, label, _ = self.control_layout.get_pointcloud_widgets_from_item(item)

        if isinstance(label, EditableLabel):
            label.enter_edit_mode(None)

    def on_remove_pointcloud_item(self, item):
        _, label, _ = self.control_layout.get_pointcloud_widgets_from_item(item)
        name = label.text

        self.control_layout.remove_pointcloud(item)

        self.viewer_layout.hide_pointcloud(name)

        self.controller.delete_pointcloud(name)
        self.info_label.setText(f"Pointcloud removed: {name}")
        self.info_label.setStyleSheet("QLabel#info_label {color: green}")

    def show_filter(self, name, box, color):
        filter_widget = FilterWidget(name)
        filter_widget.visibility_changed.connect(
            lambda visible: self.on_toggle_filter_visibility(item)
        )
        filter_widget.name_changed.connect(
            lambda new_name: self.change_filter_name(item, new_name)
        )
        filter_widget.edit_requested.connect(
            lambda: self.control_layout.edit_filter(item)
        )
        filter_widget.delete_requested.connect(lambda: self.on_remove_filter_item(item))

        item = QTreeWidgetItem()
        self.control_layout.add_filter(item, filter_widget)

        self.viewer_layout.display_filter(name, box, color.name())

        self.info_label.setText(f"Filter added: {name}")
        self.info_label.setStyleSheet("QLabel#info_label {color: green}")

    def on_remove_filter_item(self, item):
        _, label, _, _ = self.control_layout.get_filter_widgets_from_item(item)
        name = label.text

        self.control_layout.remove_filter(item)

        self.viewer_layout.hide_filter(name)

        self.controller.delete_filter(name)
        self.info_label.setText(f"Filter removed: {name}")
        self.info_label.setStyleSheet("QLabel#info_label {color: green}")

    def on_toggle_filter_visibility(self, item):
        checkbox, label, _, _ = self.control_layout.get_filter_widgets_from_item(item)
        name = label.text

        if checkbox.isChecked():
            filter = self.controller.get_filter_by_name(name)
            self.viewer_layout.display_filter(name, filter.box, filter.color.name())
            self.info_label.setText(f"Toggle filter visibility: shown ({name})")
        else:
            self.viewer_layout.hide_filter(name)
            self.info_label.setText(f"Toggle filter visibility: hidden ({name})")

        self.info_label.setStyleSheet("QLabel#info_label {color: black}")

    def toggle_filter_visibility(self, item):
        checkbox, _, _, _ = self.control_layout.get_filter_widgets_from_item(item)

        checkbox.setChecked(not checkbox.isChecked())

    def update_filter(self, old_name, new_name, box, color):
        self.viewer_layout.hide_filter(old_name)

        self.viewer_layout.display_filter(new_name, box, color.name())

        self.info_label.setText(f"Filter edited: {old_name} -> {new_name}")
        self.info_label.setStyleSheet("QLabel#info_label {color: green}")

    def change_filter_name(self, item, new_name=None):
        _, label, _, _ = self.control_layout.get_filter_widgets_from_item(item)
        name = label.text

        if new_name and new_name != name:
            is_available = self.controller.is_filter_name_available(new_name)

            if is_available:
                self.viewer_layout.change_actor_name(name, new_name)
                self.controller.rename_filter(name, new_name)
                label.apply_validated_text(new_name)
                label.setToolTip(new_name)

                self.info_label.setText(f"filter renamed: {name} -> {new_name}")
                self.info_label.setStyleSheet("QLabel#info_label {color: green}")

            else:
                label.cancel_edit()

                self.info_label.setText(f"filter name already exists: {new_name}")
                self.info_label.setStyleSheet("QLabel#info_label {color: red}")

        else:
            label.cancel_edit()

            self.info_label.setText("filter name unchanged")
            self.info_label.setStyleSheet("QLabel#info_label {color: black}")

    def trigger_filter_rename(self, item):
        _, label, _, _ = self.control_layout.get_filter_widgets_from_item(item)

        if isinstance(label, EditableLabel):
            label.enter_edit_mode(None)
