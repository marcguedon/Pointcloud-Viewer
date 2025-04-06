import numpy as np
import open3d as o3d


def main():
    nb_points = 1000
    points = np.random.uniform(low=-1.0, high=1.0, size=(nb_points, 3))

    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)

    colors = np.random.rand(nb_points, 3)
    pcd.colors = o3d.utility.Vector3dVector(colors)

    o3d.io.write_point_cloud("data/nuage_aleatoire_05.ply", pcd)


if __name__ == "__main__":
    main()
