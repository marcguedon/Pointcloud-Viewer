import numpy as np
import pyvista as pv
from pyvistaqt import QtInteractor
from PyQt5.QtWidgets import *


class ViewerLayout(QVBoxLayout):
    def __init__(self):
        super().__init__()

        self.theme = "white"
        self.show_axes = True

        self.pointclouds = {}
        self.filters = {}

        self.create_ui()

    def create_ui(self):
        self.plotter = QtInteractor()
        self.plotter.set_background("white")
        self.plotter.add_axes()
        # self.add_origin_axes(line_width=0.5)
        self.addWidget(self.plotter.interactor)

    def add_pointcloud(self, name: str, data: pv.PolyData):
        self.pointclouds[name] = data
        self.update_viewer()

    def delete_pointcloud(self, name: str):
        if name in self.pointclouds:
            del self.pointclouds[name]
        self.update_viewer()

    def change_pointcloud_name(self, old_name: str, new_name: str):
        if old_name in self.pointclouds:
            self.pointclouds[new_name] = self.pointclouds.pop(old_name)

    def add_filter(self, name: str, data: pv.PolyData, color: str):
        self.filters[name] = (data, color)
        self.update_viewer()

    def delete_filter(self, name: str):
        if name in self.filters:
            del self.filters[name]
        self.update_viewer()

    def change_filter_name(self, old_name: str, new_name: str):
        if old_name in self.filters:
            self.filters[new_name] = self.filters.pop(old_name)

    def show_hide_axes(self):
        self.show_axes = not self.show_axes

        if self.show_axes:
            self.add_origin_axes(line_width=0.5)

        else:
            self.plotter.remove_actor("origin_axes")

    def change_theme(self):
        if self.theme == "white":
            self.plotter.set_background("black")
            self.theme = "black"
        else:
            self.plotter.set_background("white")
            self.theme = "white"

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

        for filter_name, filter_data in self.filters.items():
            data, color = filter_data
            self.plotter.add_mesh(data, style="wireframe", color=color, line_width=3)

        for pointcloud_name, pointcloud_data in self.pointclouds.items():
            if self.filters:
                for filter_name, filter_data in self.filters.items():
                    data, color = filter_data

                    filtered_data = self.filter_points_inside_polygon(
                        pointcloud_data, data
                    )

                    if filtered_data.n_points > 0:
                        self.plotter.add_mesh(filtered_data, show_scalar_bar=False)

            else:
                self.plotter.add_mesh(pointcloud_data, show_scalar_bar=False)

        if self.show_axes:
            self.add_origin_axes(line_width=0.5)
        self.plotter.add_axes()

        self.plotter.camera_position = camera_position
        self.plotter.render()

    def add_origin_axes(self, scale=1.0, line_width=1.0):
        def make_arrow(direction, color):
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

        axes = x_arrow + y_arrow + z_arrow

        self.plotter.add_mesh(
            axes, scalars="colors", rgb=True, show_scalar_bar=False, name="origin_axes"
        )
