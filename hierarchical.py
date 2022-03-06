# the file is for hierarchical algorithm

import numpy as np
import heapq
import os
import scipy.spatial
import math
from scipy.spatial import distance


class bicluster:
    def __init__(self, vec, left=None, right=None, distance=0.0, id=None):
        self.left = left
        self.vec = vec
        self.right = right
        self.distance = distance
        self.id = id


class Point:
    def __init__(self, x, y, z):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)


def read_object(filename):
    point_list = []
    with open(filename, "r") as fh:
        lines = fh.readlines()
        for line in lines:
            pt_x = float(line.split(" ")[0])
            pt_y = float(line.split(" ")[1])
            pt_z = float(line.split(" ")[2].strip('\n'))
            pt = np.array((pt_x, pt_y, pt_z))
            point_list.append(pt)
    return point_list


def compute_height_difference(point_list):
    z_max = point_list[0][2]
    z_min = point_list[0][2]
    for point in point_list:
        if point[2] > z_max: z_max = point[2]
        if point[2] < z_min: z_min = point[2]
    return z_max - z_min


def convex_hull_area(point_list):
    hull = scipy.spatial.ConvexHull(point_list)
    return hull.area


def convex_hull_volume(point_list):
    hull = scipy.spatial.ConvexHull(point_list)
    return hull.volume


def point_density(point_list):
    hull = scipy.spatial.ConvexHull(point_list)
    density = len(point_list) / hull.area
    return density


def read_fold():
    path = r"C:\Users\pro\Desktop\Geomatics\Q3\ML\A1\test"
    files = os.listdir(path)
    feature_list = []
    for file in files:
        if not os.path.isdir(file):
            filename = path + "/" + file
            point_list = read_object(filename)
            z_difference = compute_height_difference(point_list)
            area = convex_hull_area(point_list)
            # volume = convex_hull_volume(point_list)
            density = point_density(point_list)
            # feature_list.append([[z_difference, area, density]])
            feature_list.append((z_difference, area, density))
    return feature_list


def create_distance_dic(feature_list):
    dist = scipy.spatial.distance.cdist(feature_list, feature_list, 'euclidean')
    dist_list = {}
    heap = []
    for i in range(len(dist)):
        for j in range(i + 1, len(dist)):
            # dist_list.append([bicluster([i, j], left=i, right=j, distance=dist[i][j])])
            dist_list[(i, j)] = dist[i][j]
            heap.append(dist[i][j])
    heapq.heapify(heap)
    return dist_list, heap


def compute_min_pair(bicluster):
    min_dist = 9999999
    size = len(bicluster)
    feature = (0, 0)
    for i in range(len(bicluster)):
        for j in range(len(bicluster)):
            if i == j:
                continue
            elif i != j:
                for i_item in bicluster[i].vec:
                    for j_item in bicluster[j].vec:
                        dist = scipy.spatial.distance.euclidean(i_item, j_item)
                        if dist == 0: continue
                        if dist < min_dist:
                            min_dist = dist
                            feature = (i, j)
    return feature


def get_keys(d, value):
    for item in d.keys():
        if d[item] == value:
            return item


def min_dist(dist_dic, heap):
    if (len(heap) != 0):
        min_dist = heapq.heappop(heap)
        key = get_keys(dist_dic, min_dist)
        return key


def hierarchical_clustering(feature_list, n_cluster):
    old_cluster = [bicluster(feature_list[i], id=i) for i in range(len(feature_list))]
    result = []
    reference = []
    dist_list, heap = create_distance_dic(feature_list)
    for i in range(len(feature_list)):
        result.append(i)
        reference.append(i)
    while len(result) > n_cluster:

        cluster_id = []
        min_key = min_dist(dist_list, heap)
        left = reference[min_key[0]]
        right = reference[min_key[1]]

        if isinstance(left, int):
            cluster_id.append(left)
        else:
            for item in left:
                cluster_id.append(item)
        if isinstance(right, int):
            cluster_id.append(right)
        else:
            for item in right:
                cluster_id.append(item)

        for i in range(len(result)):
            if result[i] == reference[min_key[1]]:
                del result[i]
                break
        for i in range(len(result)):
            if result[i] == reference[min_key[0]]:
                del result[i]
                break
        result.append(cluster_id)

        for k in range(len(cluster_id)):
            for l in range(len(reference)):
                if l == cluster_id[k]:
                    reference[l] = cluster_id
    return result


def find_location(min_key, result):
    for i in range(len(result)):
        if isinstance(result[i], int):
            if result[i] == min_key:
                return i
        else:
            for j in range(len(result[i])):
                if result[i][j] == min_key:
                    return i


def new_cluster(min_key, result):
    cluster_id = []

    left = find_location(min_key[0], result)
    right = find_location(min_key[1], result)

    if isinstance(result[left], int):
        cluster_id.append(result[left])
    else:
        for item in result[left]:
            cluster_id.append(item)

    if isinstance(result[right], int):
        cluster_id.append(result[right])
    else:
        for item in result[right]:
            cluster_id.append(item)
    return cluster_id


def hier2(feature_list, n_cluster):
    old_cluster = [bicluster(i, id=i) for i in range(len(feature_list))]

    result = []
    dist_list, heap = create_distance_dic(feature_list)
    for i in range(len(feature_list)):
        result.append(i)

    while len(result) > n_cluster:
        min_key = min_dist(dist_list, heap)
        left = find_location(min_key[0], result)
        right = find_location(min_key[1], result)
        if left == right:
            continue
        else:
            cluster_id = new_cluster(min_key, result)

            if (left > right):
                del result[left]
                del result[right]
            else:
                del result[right]
                del result[left]

            result.append(cluster_id)
    return result


if __name__ == '__main__':
    feature_list = read_fold()
    # feature=[(1,1,1),(4,4,4),(2,2,2),(112,113,115),(113,112,115),(50,60,70),(51,66,77)]
    cluster = hier2(feature_list, 4)
    for item in cluster:
        print(item)
        print("next:")
    print("finish")
