import open3d as o3d
from threading import Thread
from open3d.visualization import gui, rendering


class Open3DViewer:
    def __init__(self, data_manager, width=1920, height=1080, title="Open3D Viewer"):
        self.data_manager = data_manager

        gui.Application.instance.initialize()
        self.window = gui.Application.instance.create_window(title, width, height)

        self.geometry_names = set()
        self.cloud_items = {}
        self.pointclouds_to_remove = []
        self.filters_to_remove = []

        self.update_thread = Thread(target=self.update_deleted_items)
        self.update_thread.start()

        self.create_ui()

    def update_deleted_items(self):
        while True:
            for name in self.pointclouds_to_remove:
                self.data_manager.remove_pointcloud(name)
                self.remove_geometry(name)
                self.pointcloud_tree.remove_item(self.cloud_items[name])
                self.cloud_items.pop(name)

                self.pointclouds_to_remove.remove(name)

            for name in self.filters_to_remove:
                self.data_manager.remove_filter(name)
                self.remove_geometry(name)
                self.filter_tree.remove_item(self.cloud_items[name])
                self.cloud_items.pop(name)

                self.filters_to_remove.remove(name)

    def create_ui(self):
        self.panel = gui.Vert(spacing=5, margins=gui.Margins(5, 5, 5, 5))

        # Pointcloud panel
        pointcloud_panel = gui.CollapsableVert("Pointclouds", spacing=5)
        add_pointcloud_button = gui.Button("Add pointCloud")
        add_pointcloud_button.tooltip = "Add pointcloud from file"
        add_pointcloud_button.vertical_padding_em = 0.1
        add_pointcloud_button.set_on_clicked(self.on_add_pointcloud_button_clicked)
        pointcloud_panel.add_child(add_pointcloud_button)

        self.pointcloud_tree = gui.TreeView()
        pointcloud_panel.add_child(self.pointcloud_tree)

        self.panel.add_child(pointcloud_panel)

        # Filter panel
        filter_panel = gui.CollapsableVert("Filters", spacing=5)
        add_filter_button = gui.Button("Add Filter")
        add_filter_button.vertical_padding_em = 0.1
        add_filter_button.set_on_clicked(self.on_add_filter_button_clicked)
        filter_panel.add_child(add_filter_button)

        self.filter_tree = gui.TreeView()
        filter_panel.add_child(self.filter_tree)

        self.panel.add_child(filter_panel)

        # Close button
        quit_button = gui.Button("Quit")
        quit_button.set_on_clicked(self.close)
        self.panel.add_child(quit_button)

        # Scene panel
        self.scene = gui.SceneWidget()
        self.scene.scene = rendering.Open3DScene(self.window.renderer)
        self.scene.scene.set_background([0, 0, 0, 1])

        self.window.add_child(self.panel)
        self.window.add_child(self.scene)

    def on_add_pointcloud_button_clicked(self):
        try:
            dialog = gui.FileDialog(
                gui.FileDialog.OPEN,
                "Open a pointcloud file",
                self.window.theme,
            )
            dialog.set_on_cancel(self.on_cancel)
            dialog.set_on_done(self.on_file_chosen)
            dialog.add_filter(".ply .pcd .xyz", "PointCloud Files (.ply, .pcd, .xyz)")

            self.window.show_dialog(dialog)
        except Exception as e:
            raise (f"Error selecting file: {e}")

    def on_add_filter_button_clicked(self):
        try:
            dialog = gui.Dialog("Create a pointcloud filter")
            panel = gui.Vert(spacing=5, margins=gui.Margins(5, 5, 5, 5))

            panel.add_child(gui.Label("Filter's name:"))

            filter_name_input = gui.TextEdit()
            filter_name_input.text_value = "Filter's name"
            panel.add_child(filter_name_input)

            buttons_panel = gui.Horiz(spacing=20, margins=gui.Margins(0, 0, 0, 0))

            cancel_button = gui.Button("Cancel")
            cancel_button.set_on_clicked(self.on_cancel)
            buttons_panel.add_child(cancel_button)

            create_button = gui.Button("Create")
            create_button.set_on_clicked(lambda: self.on_create_filter())
            buttons_panel.add_child(create_button)

            panel.add_child(buttons_panel)

            dialog.add_child(panel)

            self.window.show_dialog(dialog)
        except Exception as e:
            raise (f"Error: {e}")

    def on_cancel(self):
        self.window.close_dialog()

    def on_create_filter(self):
        self.window.close_dialog()

        try:
            name = None
        except Exception as e:
            raise (f"Error creating filter: {e}")

        self.add_filter_ui_entry(name)

    def on_file_chosen(self, filename):
        self.window.close_dialog()

        try:
            pointcloud = o3d.io.read_point_cloud(filename)
            name = self.data_manager.add_pointcloud(filename, pointcloud)
        except Exception as e:
            raise (f"Error loading pointcloud: {e}")

        self.add_cloud_ui_entry(name)

    def add_geometry(self, name, geometry):
        self.scene.scene.add_geometry(name, geometry, rendering.MaterialRecord())
        self.geometry_names.add(name)

    def remove_geometry(self, name):
        if name in self.geometry_names:
            self.scene.scene.remove_geometry(name)
            self.geometry_names.remove(name)

    def add_cloud_ui_entry(self, name):
        max_label_length = 20

        row = gui.Horiz(spacing=5, margins=gui.Margins(0, 2, 2, 2))

        # Checkbox to toggle visibility
        checkbox = gui.Checkbox("")
        checkbox.tooltip = "Toggle pointcloud visibility"
        checkbox.checked = True

        def on_toggle(checked):
            self.data_manager.set_visibility(name, checked)

            if checked:
                self.add_geometry(name, self.data_manager.get_pointcloud(name))

            else:
                self.remove_geometry(name)

        checkbox.set_on_checked(on_toggle)
        row.add_child(checkbox)

        if len(name) > max_label_length:
            label_text = name[:max_label_length] + "..."
        else:
            label_text = name

        label = gui.Label(label_text)
        label.tooltip = name
        row.add_child(label)

        # Delete button
        delete_button = gui.Button("X")
        # delete_button.background_color = o3d.visualization.gui.Color(1, 0, 0, 1)
        delete_button.tooltip = "Delete pointcloud"
        delete_button.horizontal_padding_em = 0.2
        delete_button.vertical_padding_em = 0
        delete_button.set_on_clicked(lambda: self.on_delete_cloud(name))
        row.add_child(delete_button)

        # Add the row to the tree
        item_index = self.pointcloud_tree.add_item(0, row)
        self.cloud_items[name] = item_index

        # Add the point cloud to the scene
        self.add_geometry(name, self.data_manager.get_pointcloud(name))

    def add_filter_ui_entry(self, name):
        max_label_length = 20

        row = gui.Horiz(spacing=5, margins=gui.Margins(0, 2, 2, 2))

        # Button to modify filter
        modify_button = gui.Button("Modify")

        # Checkbox to toggle visibility
        checkbox = gui.Checkbox("")
        checkbox.tooltip = "Toggle filter visibility"
        checkbox.checked = True
        
        def on_toggle(checked):
            self.data_manager.set_visibility(name, checked)

            if checked:
                self.add_geometry(name, self.data_manager.get_filter(name))

            else:
                self.remove_geometry(name)

        checkbox.set_on_checked(on_toggle)
        row.add_child(checkbox)

    def on_delete_cloud(self, name):
        self.pointclouds_to_remove.append(name)

    def build_layout(self, context):
        content_rect = self.window.content_rect
        panel_width = 230
        self.panel.frame = gui.Rect(
            content_rect.x, content_rect.y, panel_width, content_rect.height
        )
        self.scene.frame = gui.Rect(
            content_rect.x + panel_width,
            content_rect.y,
            content_rect.width - panel_width,
            content_rect.height,
        )

    def run(self):
        self.window.set_on_layout(self.build_layout)

        gui.Application.instance.run()

    def close(self):
        gui.Application.instance.quit()
