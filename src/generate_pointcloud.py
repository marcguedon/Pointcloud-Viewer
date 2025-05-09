import argparse
import numpy as np
import open3d as o3d


def generate_random_pointcloud(
    nb_points: int = 1000, colors: bool = False
) -> tuple[np.ndarray, np.ndarray | None]:
    pointcloud = np.random.uniform(low=-1.0, high=1.0, size=(nb_points, 3))
    pcd_colors = None

    if colors:
        pcd_colors = np.random.rand(nb_points, 3)

    return pointcloud, pcd_colors


def pointcloud_to_open3d_pointcloud(
    pointcloud: np.ndarray, colors: np.ndarray | None = None
) -> o3d.geometry.PointCloud:
    open3d_pointcloud = o3d.geometry.PointCloud()
    open3d_pointcloud.points = o3d.utility.Vector3dVector(pointcloud)

    if colors is not None:
        open3d_pointcloud.colors = o3d.utility.Vector3dVector(colors)

    return open3d_pointcloud


def main(filename: str, nb_points: int = 1000, colors: bool = False):
    pointcloud, colors = generate_random_pointcloud(nb_points, colors)
    # np.save(filename, pointcloud)
    
    poincloud_object = pointcloud_to_open3d_pointcloud(pointcloud, colors)
    o3d.io.write_point_cloud(filename, poincloud_object)


if __name__ == "__main__":
    arg = argparse.ArgumentParser()
    arg.add_argument(dest="filename", type=str, help="Output filename")
    arg.add_argument(
        "-n",
        "--nb_points",
        type=int,
        default=1000,
        help="Number of points in the pointcloud",
    )
    arg.add_argument(
        "-c",
        "--colors",
        action="store_true",
        help="Generate random colors for the points",
    )

    args = arg.parse_args()

    main(args.filename, args.nb_points, args.colors)
