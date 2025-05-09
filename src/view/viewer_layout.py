import numpy as np
import pyvista as pv
from pyvistaqt import QtInteractor
from PyQt5.QtWidgets import QVBoxLayout
from controller.controller import Controller
from model.filter import Filter
from model.pointcloud import Pointcloud
from utils.log import Log
from utils.theme import Theme


def get_origin_axis(scale: float = 1.0, line_width: float = 1.0) -> pv.Arrow:
    def make_arrow(
        direction: tuple[int, int, int], color: tuple[int, int, int]
    ) -> pv.Arrow:
        arrow = pv.Arrow(
            start=(0, 0, 0),
            direction=direction,
            tip_length=0.3 * line_width,
            tip_radius=0.05 * line_width,
            shaft_radius=0.02 * line_width,
            scale=scale,
        )
        nb_points = arrow.n_points
        colors = np.tile(np.array(color), (nb_points, 1))
        arrow["colors"] = colors

        return arrow

    x_arrow = make_arrow((1, 0, 0), (255, 0, 0))
    y_arrow = make_arrow((0, 1, 0), (0, 255, 0))
    z_arrow = make_arrow((0, 0, 1), (0, 0, 255))

    axis = x_arrow + y_arrow + z_arrow

    return axis


class ViewerLayout(QVBoxLayout):
    def __init__(self):
        super().__init__()

        self.controller: Controller = Controller()
        self.controller.change_theme_signal.connect(self.change_theme)
        self.controller.show_hide_axes_signal.connect(self.show_hide_axes)

        self.controller.add_pointcloud_signal.connect(self.add_pointcloud)
        self.controller.delete_pointcloud_signal.connect(self.remove_pointcloud)
        self.controller.toggle_pointcloud_visibility_signal.connect(
            self.toggle_pointcloud_visibility
        )

        self.controller.update_socket_pointcloud_signal.connect(
            self.update_socket_pointcloud
        )
        self.controller.client_disconnected_signal.connect(self.remove_stock_pointcloud)
        self.controller.stop_socket_signal.connect(self.remove_stock_pointcloud)

        self.controller.add_filter_signal.connect(self.add_filter)
        self.controller.delete_filter_signal.connect(self.remove_filter)
        self.controller.toggle_filter_visibility_signal.connect(
            self.toggle_filter_visibility
        )
        self.controller.update_filter_signal.connect(self.update_viewer)

        self.show_axes: bool = False
        self.axes: pv.Arrow = get_origin_axis(line_width=0.5)

        self.pointclouds_list: list[Pointcloud] = []
        self.filters_list: list[Filter] = []
        self.socket_pointcloud: pv.PolyData = None

        self.create_ui()

    def create_ui(self):
        self.setContentsMargins(0, 0, 0, 0)

        self.plotter = QtInteractor()
        self.plotter.set_background("white")
        self.plotter.add_axes()
        # self.add_origin_axes(line_width=0.5)
        self.addWidget(self.plotter.interactor)

    # POINTCLOUDS
    def add_pointcloud(self, pointcloud: Pointcloud):
        self.pointclouds_list.append(pointcloud)
        self.update_viewer()

    def remove_pointcloud(self, pointcloud_to_remove: Pointcloud):
        try:
            self.pointclouds_list.remove(pointcloud_to_remove)

            self.update_viewer()
        except ValueError:
            self.controller.notify(
                Log.ERROR, f"Pointcloud not found: {pointcloud_to_remove}"
            )

    def toggle_pointcloud_visibility(self, pointcloud: Pointcloud, is_visible: bool):
        if is_visible:
            self.add_pointcloud(pointcloud)

        else:
            self.remove_pointcloud(pointcloud)

    # FILTERS
    def add_filter(self, filter: Filter):
        self.filters_list.append(filter)
        self.update_viewer()

    def remove_filter(self, filter_to_remove: Filter):
        try:
            self.filters_list.remove(filter_to_remove)

            self.update_viewer()
        except ValueError:
            self.controller.notify(
                Log.ERROR, f"Filter not found: {filter_to_remove.name}"
            )

    def toggle_filter_visibility(self, filter: Filter, is_visible: bool):
        if is_visible:
            self.add_filter(filter)

        else:
            self.remove_filter(filter)

    # UTILITY
    def show_hide_axes(self):
        self.show_axes = not self.show_axes

        if self.show_axes:
            self.add_origin_axis()

        else:
            self.plotter.remove_actor("origin_axes")

    def change_theme(self, theme: Theme):
        self.plotter.set_background(theme.value)

    def clear_viewer(self):
        self.plotter.clear()

    def filter_points_inside_polygon(
        self, pointcloud: pv.PolyData, box: pv.PolyData
    ) -> pv.PolyData:
        enclosed = pointcloud.select_enclosed_points(box, check_surface=False)

        return pointcloud.extract_points(enclosed["SelectedPoints"] == 1)

    def update_viewer(self):
        camera_position = self.plotter.camera_position

        self.clear_viewer()

        for filter in self.filters_list:
            self.plotter.add_mesh(
                filter.box, style="wireframe", color=filter.color, line_width=3
            )

        pointclouds_list: list[pv.PolyData] = [
            pointcloud.points for pointcloud in self.pointclouds_list
        ]

        if self.socket_pointcloud is not None:
            pointclouds_list.append(self.socket_pointcloud)

        for pointcloud in pointclouds_list:
            if self.filters_list:
                for filter in self.filters_list:
                    filtered_pointcloud = self.filter_points_inside_polygon(
                        pointcloud, filter.box
                    )

                    if filtered_pointcloud.n_points > 0:
                        self.plotter.add_mesh(
                            filtered_pointcloud, show_scalar_bar=False
                        )

            else:
                self.plotter.add_mesh(pointcloud, show_scalar_bar=False)

        if self.show_axes:
            self.add_origin_axis()

        self.plotter.add_axes()
        self.plotter.camera_position = camera_position
        self.plotter.render()

    def add_origin_axis(self):
        self.plotter.add_mesh(
            self.axes,
            scalars="colors",
            rgb=True,
            show_scalar_bar=False,
            name="origin_axes",
        )

    def update_socket_pointcloud(self, pointcloud: pv.PolyData):
        self.socket_pointcloud = pointcloud
        self.update_viewer()

    def remove_stock_pointcloud(self):
        if self.socket_pointcloud is not None:
            self.socket_pointcloud = None
            self.update_viewer()
