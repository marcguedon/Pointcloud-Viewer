import os
import yaml
import pyvista as pv
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtCore import pyqtSignal, QObject
from controller.pointcloud_service import PointcloudService
from controller.filter_service import FilterService
from view.help_window import HelpWindow
from model.pointcloud import Pointcloud
from model.filter import Filter
from utils.log import Log
from utils.theme import Theme


class Controller(QObject):
    _instance = None

    notify_signal = pyqtSignal(Log, str)
    close_application_signal = pyqtSignal()
    change_theme_signal = pyqtSignal(Theme)
    show_hide_axes_signal = pyqtSignal()

    open_socket_window_signal = pyqtSignal()
    start_socket_signal = pyqtSignal(int, int)
    update_socket_pointcloud_signal = pyqtSignal(pv.PolyData)
    client_disconnected_signal = pyqtSignal()
    pause_socket_signal = pyqtSignal()
    stop_socket_signal = pyqtSignal()

    open_debug_window_signal = pyqtSignal()

    add_pointcloud_signal = pyqtSignal(Pointcloud)
    delete_pointcloud_signal = pyqtSignal(Pointcloud)
    toggle_pointcloud_visibility_signal = pyqtSignal(Pointcloud, bool)

    add_filter_signal = pyqtSignal(Filter)
    delete_filter_signal = pyqtSignal(Filter)
    toggle_filter_visibility_signal = pyqtSignal(Filter, bool)
    edit_filter_signal = pyqtSignal(Filter)
    update_filter_signal = pyqtSignal(Filter)

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(Controller, cls).__new__(cls)
            cls._instance._initialized = False

        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        super().__init__()
        self._initialized = True

        self.pointcloud_srv = PointcloudService()
        self.filter_srv = FilterService()

        self.pointclouds_list: list[Pointcloud] = []
        self.filters_list: list[Filter] = []

        self.help_window = None

        self.theme: Theme = Theme.LIGHT_MODE

    # APPLICATION
    def notify(self, log: Log, message: str):
        self.notify_signal.emit(log, message)

    def close_application(self):
        if self.help_window is not None:
            self.help_window.close()

        self.close_application_signal.emit()

    def change_theme(self):
        if self.theme == Theme.LIGHT_MODE:
            self.theme = Theme.DARK_MODE
        else:
            self.theme = Theme.LIGHT_MODE

        self.change_theme_signal.emit(self.theme)
        self.notify(Log.INFO, f"Theme changed to: {self.theme}")

    def show_hide_axes(self):
        self.show_hide_axes_signal.emit()
        self.notify(Log.INFO, "Axes visibility toggled")

    def open_help(self):
        if self.help_window is None:
            self.help_window = HelpWindow()

        self.help_window.show()
        self.help_window.raise_()

    # SOCKET
    def open_socket_window(self):
        self.open_socket_window_signal.emit()

    def start_socket(self, port: int, persistence: int):
        self.start_socket_signal.emit(port, persistence)

    def update_socket_pointcloud(self, pointcloud: Pointcloud):
        self.update_socket_pointcloud_signal.emit(pointcloud)
        self.notify(
            Log.DEBUG,
            f"Pointcloud received from socket: {len(pointcloud.points)} points",
        )

    def client_disconnected(self):
        self.client_disconnected_signal.emit()
        self.notify(Log.INFO, "Client disconnected")

    def pause_socket(self):
        self.pause_socket_signal.emit()
        self.notify(Log.SUCCESS, "Pausing socket")

    def stop_socket(self):
        self.stop_socket_signal.emit()
        self.notify(Log.SUCCESS, "Stopping socket")

    # DEBUG
    def open_debug_window(self):
        self.open_debug_window_signal.emit()

    # POINTCLOUDS
    def load_pointclouds(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            caption="Load pointclouds",
            directory="",
            filter="Pointcloud files (*.ply *.pcd *.xyz);;Numpy files (*.npy *.npz);;All files (*)",
        )

        if not file_paths:
            self.notify(Log.INFO, "No file selected")
            return

        for file_path in file_paths:
            if not os.path.exists(file_path):
                self.notify(Log.ERROR, f"File not found: {file_path}")
                continue

            if not file_path.endswith((".ply", ".pcd", ".xyz", ".npy", ".npz")):
                self.notify(
                    Log.WARNING,
                    f"Invalid file format. PLY, PCD, XYZ, NPY and NPZ files are supported ({os.path.basename(file_path)})",
                )
                continue

            try:
                name, pointcloud_data = (
                    self.pointcloud_srv.get_pointcloud_data_from_path(
                        self.pointclouds_list, file_path
                    )
                )
            except ValueError as e:
                self.notify(Log.ERROR, f"Error: {str(e)}")
                continue

            pointcloud = Pointcloud(name, pointcloud_data)
            self.pointclouds_list.append(pointcloud)

            self.add_pointcloud_signal.emit(pointcloud)

            self.notify(
                Log.SUCCESS,
                f"Pointcloud loaded: {pointcloud.name} ({pointcloud.points.n_points} points)",
            )

    def delete_pointcloud(self, pointcloud_to_delete: Pointcloud):
        try:
            self.pointclouds_list.remove(pointcloud_to_delete)
            self.delete_pointcloud_signal.emit(pointcloud_to_delete)
            self.notify(Log.SUCCESS, f"Pointcloud removed: {pointcloud_to_delete.name}")
        except ValueError:
            self.notify(Log.ERROR, f"Pointcloud not found: {pointcloud_to_delete.name}")

    def toggle_pointcloud_visibility(self, pointcloud: Pointcloud, is_visible: bool):
        self.toggle_pointcloud_visibility_signal.emit(pointcloud, is_visible)

        state = "shown" if is_visible else "hidden"
        self.notify(
            Log.DEBUG, f"Toggle pointcloud visibility: {state} ({pointcloud.name})"
        )

    def rename_pointcloud(self, pointcloud: Pointcloud, new_name: str):
        if new_name != pointcloud.name:
            if self.is_pointcloud_name_available(new_name):
                self.notify(
                    Log.SUCCESS, f"Pointcloud renamed: {pointcloud.name} -> {new_name}"
                )
                pointcloud.name = new_name
                return True

            else:
                self.notify(Log.WARNING, f"Pointcloud name already exists: {new_name}")
                return False

        else:
            self.notify(Log.INFO, "Pointcloud name unchanged")
            return False

    def is_pointcloud_name_available(self, name):
        return all(pointcloud.name != name for pointcloud in self.pointclouds_list)

    # FILTERS
    def add_filter(
        self,
        name: str,
        bounds: tuple[float, float, float, float, float, float],
        color: str,
    ) -> Filter:
        name = self.filter_srv.get_filter_name_from_str(self.filters_list, name)

        filter = Filter(name, bounds, color)
        self.filters_list.append(filter)

        self.add_filter_signal.emit(filter)

        self.notify(Log.SUCCESS, f"Filter added: {filter.name}")

    def delete_filter(self, filter_to_delete: Filter):
        try:
            self.filters_list.remove(filter_to_delete)
            self.delete_filter_signal.emit(filter_to_delete)
            self.notify(Log.SUCCESS, f"Filter removed: {filter_to_delete.name}")
        except ValueError:
            self.notify(Log.ERROR, f"Filter not found: {filter_to_delete.name}")

    def toggle_filter_visibility(self, filter: Filter, is_visible: bool):
        self.toggle_filter_visibility_signal.emit(filter, is_visible)

        state = "shown" if is_visible else "hidden"
        self.notify(Log.DEBUG, f"Toggle filter visibility: {state} ({filter.name})")

    def rename_filter(self, filter: Filter, new_name: str):
        if new_name != filter.name:
            if self.is_filter_name_available(new_name):
                self.notify(Log.SUCCESS, f"Filter renamed: {filter.name} -> {new_name}")
                filter.name = new_name
                self.update_filter_signal.emit(filter)

                return True

            else:
                self.notify(Log.WARNING, f"Filter name already exists: {new_name}")

        else:
            self.notify(Log.INFO, "Filter name unchanged")

        return False

    def is_filter_name_available(self, name):
        return all(filter.name != name for filter in self.filters_list)

    def edit_filter(self, filter: Filter):
        self.edit_filter_signal.emit(filter)

    def set_filter_bounds(
        self, filter: Filter, bounds: tuple[float, float, float, float, float, float]
    ):
        filter.box = bounds
        self.update_filter_signal.emit(filter)
        self.notify(Log.DEBUG, f"{filter.name} filter bounds changed to : {bounds}")

    def set_filter_color(self, filter: Filter, color: str):
        filter.color = color
        self.update_filter_signal.emit(filter)
        self.notify(Log.DEBUG, f"{filter.name} filter color changed to : {color}")

    def import_filter(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            caption="Import filters",
            directory="",
            filter="YAML files (*.yaml *.yml);;All files (*)",
        )

        if not file_paths:
            self.notify(Log.INFO, "No file selected")
            return

        for file_path in file_paths:
            if not os.path.exists(file_path):
                self.notify(Log.ERROR, f"File not found: {file_path}")
                continue

            if not file_path.endswith((".yaml", ".yml")):
                self.notify(
                    Log.WARNING,
                    f"Invalid file format. Only YAML files are supported ({os.path.basename(file_path)})",
                )
                continue

            with open(file_path, "r", encoding="UTF-8") as file:
                filters_dict = yaml.safe_load(file)

            for filter_name, filter_data in filters_dict["filters"].items():
                bounds = filter_data["bounds"]
                filter_color = filter_data["color"]

                self.add_filter(filter_name, bounds, filter_color)

            self.notify(
                Log.SUCCESS,
                f"Filters imported successfully: {os.path.basename(file_path)}",
            )

    def export_filter(self):
        if not self.filters_list:
            self.notify(Log.INFO, "No filters to export")
            return

        dialog = QFileDialog(caption="Export filters")
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
                    None,
                    "File exists",
                    f"The file {os.path.basename(file_path)} already exists.<br>Do you want to overwrite it?",
                    buttons=QMessageBox.Yes | QMessageBox.No,
                    defaultButton=QMessageBox.No,
                )
                if reply != QMessageBox.Yes:
                    self.notify(Log.INFO, "Export cancelled")
                    return

            filters_dict = {
                "filters": {
                    filter.name: {
                        "bounds": [round(val, 2) for val in filter.box.bounds],
                        "color": filter.color,
                    }
                    for filter in self.filters_list
                }
            }

            with open(file_path, "w", encoding="UTF-8") as file:
                yaml.dump(filters_dict, file)

            self.notify(
                Log.SUCCESS,
                f"Filters exported successfully: {os.path.basename(file_path)}",
            )
