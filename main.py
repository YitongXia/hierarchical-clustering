import hierarchical as h
import numpy as np
import os
import laspy
from scipy.spatial import ConvexHull
from itertools import repeat


def compute_height_difference(point_list):
    z_max, z_min = point_list[0][2], point_list[0][2]
    for point in point_list:
        if point[2] > z_max:
            z_max = point[2]
        if point[2] < z_min:
            z_min = point[2]
    return float(z_max) - float(z_min)


def convex_hull_area(point_list):
    hull = ConvexHull(point_list)
    return hull.area


def convex_hull_volume(point_list):
    hull = ConvexHull(point_list)
    return hull.volume


def density(object, area):
    dens = (len(object) / area)
    return dens


def vol_density(object, volume):
    dens = (len(object) / volume)
    return dens


def squareness(object):
    x_max, x_min = float(object[0][0]), float(object[0][0])
    y_max, y_min = float(object[0][1]), float(object[0][1])

    for point in object:
        if float(point[0]) > x_max:
            x_max = float(point[0])
        if float(point[0]) < x_min:
            x_min = float(point[0])
        if float(point[1]) > y_max:
            y_max = float(point[1])
        if float(point[1]) < y_min:
            y_min = float(point[1])

    x_dis = x_max - x_min
    y_dis = y_max - y_min
    if x_dis > y_dis:
        return x_dis / y_dis
    else:
        return y_dis / x_dis


def length(object):
    x_max, x_min = float(object[0][0]), float(object[0][0])
    y_max, y_min = float(object[0][1]), float(object[0][1])

    for point in object:
        if float(point[0]) > x_max:
            x_max = float(point[0])
        if float(point[0]) < x_min:
            x_min = float(point[0])
        if float(point[1]) > y_max:
            y_max = float(point[1])
        if float(point[1]) < y_min:
            y_min = float(point[1])

    x_dis = x_max - x_min
    y_dis = y_max - y_min
    if x_dis > y_dis:
        return x_dis
    else:
        return y_dis


def file_write(all_x, all_y, all_z, clusters, output_file):
    # write to file
    # Create a new header
    header = laspy.LasHeader(point_format=3, version="1.2")
    header.add_extra_dim(laspy.ExtraBytesParams(name="random", type=np.float32))
    # header.offsets = np.min(accumulated_objects, axis=0)
    header.scales = np.array([0.1, 0.1, 0.1])

    # Create a Las
    las = laspy.LasData(header)

    # create new dimension for cluster values
    las.add_extra_dim(laspy.ExtraBytesParams(
        name="clusters",
        type=np.uint64,
    ))

    # add all coordinates to the las file
    las.x = np.array(all_x).astype(np.float64)
    las.y = np.array(all_y).astype(np.float64)
    las.z = np.array(all_z).astype(np.float64)
    las.clusters = clusters

    # write the output to the file
    las.write(output_file)


if __name__ == '__main__':
    input_folder = (
        r"C:\Users\pro\Desktop\Geomatics\Q3\ML\A1\test")
    all_point_list = []
    feauture_points = []
    points_per_object = []
    all_x = []
    all_y = []
    all_z = []
    for file in os.listdir(input_folder):
        file_points = []
        with open(os.path.join(input_folder, file), 'r') as f:
            for points in f:
                split = points.split()
                all_x.append(split[0])
                all_y.append(split[1])
                all_z.append(split[2])
                all_point_list.append(split)
                file_points.append(split)
            points_per_object.append(file_points)

    # accumulated_points = np.array(all_point_list).astype(np.float64)

    # values for each of the object
    object_values = []

    # object size of each object
    object_size = []
    for object in points_per_object:
        area = convex_hull_area(object)
        volume = convex_hull_volume(object)
        height_diff = compute_height_difference(object)
        dens = density(object, area)
        leng = length(object)
        squared = squareness(object)
        vol_dens = vol_density(object, volume)

        # append the values to object_values to perform the clustering on
        # object_values.append([area, volume, height_diff, dens, leng, squared])
        object_values.append([dens, vol_dens])
        # append the amount of points of the objects, so later we can use this amount of points to link points to a cluster
        object_size.append(len(object))

    object_points = np.array(object_values).astype(np.float64)

    hcluster=h.hier2(object_points,4)
    for object in hcluster:
        print(object)

