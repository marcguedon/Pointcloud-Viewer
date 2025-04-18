from pyvistaqt import QtInteractor
from PyQt5.QtWidgets import *


class ViewerLayout(QVBoxLayout):
    def __init__(self):
        super().__init__()

        self.plotter_actors = {}
        self.theme = "white"

        self.create_ui()

    def create_ui(self):
        self.plotter = QtInteractor()
        self.plotter.set_background("white")
        self.addWidget(self.plotter.interactor)

    def change_actor_name(self, old_name, new_name):
        self.plotter_actors[new_name] = self.plotter_actors.pop(old_name)
        self.plotter_actors[new_name].name = new_name

    def display_pointcloud(self, name, data):
        actor = self.plotter.add_mesh(data, show_scalar_bar=False)
        self.plotter_actors[name] = actor

    def hide_pointcloud(self, name):
        self.plotter.remove_actor(self.plotter_actors[name])
        self.plotter_actors.pop(name)

    def display_filter(self, name, data, color):
        actor = self.plotter.add_mesh(
            data, style="wireframe", color=color, line_width=3
        )
        self.plotter_actors[name] = actor

    def hide_filter(self, name):
        self.plotter.remove_actor(self.plotter_actors[name])
        self.plotter_actors.pop(name)

    def change_theme(self):
        if self.theme == "white":
            self.plotter.set_background("black")
            self.theme = "black"
        else:
            self.plotter.set_background("white")
            self.theme = "white"
