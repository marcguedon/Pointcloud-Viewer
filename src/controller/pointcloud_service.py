import os
import numpy as np
import pyvista as pv
from model.pointcloud import Pointcloud


class PointcloudService:
    def __init__(self):
        pass

    def get_pointcloud_data_from_path(
        self, pointcloud_list: list[Pointcloud], path: str
    ) -> tuple[str, pv.PolyData]:
        pointcloud_data = None

        if path.endswith((".ply", ".pcd", ".xyz")):
            pointcloud_data = pv.read(path)

        else:  # ".npy" or ".npz" file format
            data = np.load(path)

            if data.ndim == 2 and data.shape[1] == 3:
                pointcloud_data = pv.PolyData(data)

            else:
                raise ValueError(
                    f"Invalid data shape: {data.shape}. Expected (N, 3)."
                )

        name = self.get_pointcloud_name_from_path(pointcloud_list, path)

        return name, pointcloud_data

    def get_pointcloud_name_from_path(
        self, pointclouds_list: list[Pointcloud], path: str
    ) -> str:
        name = self.extract_name(path)

        existing_names = {pointcloud.name for pointcloud in pointclouds_list}
        original_filename = name
        count = 1

        while name in existing_names:
            name = f"{original_filename}_{count}"
            count += 1

        return name

    def extract_name(self, path: str) -> str:
        return os.path.splitext(os.path.basename(path))[0]
