import numpy as np
import math


def distance(point, profile):
    point = point.np
    start = profile.start.np
    end = profile.end.np

    line_vec = end - start
    point_vec = point - start
    cross_product = np.cross(line_vec, point_vec)
    distance = np.linalg.norm(cross_product) / np.linalg.norm(line_vec)
    return distance


def distance_2pt(point1, point2):
    # define two points
    point1np = point1.np
    point2np = point2.np

    # calculate the Euclidean distance between the two points
    pt_distance = np.linalg.norm(point2np - point1np)
    return pt_distance


def distance_point_to_line(point, profile):
    # Convert inputs to numpy arrays for easier math operations
    point = point.np

    line_start = profile.start.np
    line_end = profile.end.np

    # Calculate the vector V between the start and end points of the line
    V = line_end - line_start

    # Calculate the vector W between the start point of the line and the given point
    W = point - line_start

    # Project vector W onto vector V using dot product
    projection = np.dot(W, V) / np.dot(V, V)

    # Calculate the closest point on the line
    closest_point = line_start + projection * V

    # Calculate the distance between the point and the line
    distance = np.linalg.norm(point - closest_point)

    return distance, closest_point


class Point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.np = np.array([x, y, z])
        self.name = ""

    def __str__(self):
        return f'{round(self.x, 1):>8}, {round(self.y, 1):>8}, {round(self.z, 1):>8}'


class Vector:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.np = np.array([x, y, z])
        self.normalize()

    def normalize(self):
        length = np.linalg.norm(self.np)
        v_norm = self.np / length
        self.x = v_norm[0]
        self.y = v_norm[1]
        self.z = v_norm[2]
        self.np = v_norm

    def __str__(self):
        return f'{self.x}, {self.y}, {self.z}'


class Plane:
    def __init__(self, origin, x, y):
        self.origin = origin
        self.x_vector = x
        self.y_vector = y

    def __str__(self):
        return f'Origin {self.origin} | X: {self.x_vector} | Y: {self.y_vector}'

    def get_origin_str(self):
        return f'{self.origin.x},{self.origin.y},{self.origin.z}'

    def get_x_vec_str(self):
        return f'{self.x_vector.x},{self.x_vector.y},{self.x_vector.z}'

    def get_y_vec_str(self):
        return f'{self.y_vector.x},{self.y_vector.y},{self.y_vector.z}'


def get_local_coordinate(point: Point,
                         plane: Plane,
                         origin_x: Vector = Vector(1, 0, 0),
                         origin_y: Vector = Vector(0, 1, 0), ):
    vectors = []

    destination_x = plane.x_vector
    destination_y = plane.y_vector

    global_origin = plane.origin

    origin_z = np.cross(origin_x.np, origin_y.np)
    destination_z = np.cross(destination_x.np, destination_y.np)
    vectors.append(origin_x.np)
    vectors.append(origin_y.np)
    vectors.append(origin_z)
    vectors.append(destination_x.np)
    vectors.append(destination_y.np)
    vectors.append(destination_z)

    normalized_vectors = []

    for vector in vectors:
        length = np.linalg.norm(vector)
        v_norm = vector / length

        normalized_vectors.append(v_norm)

    # Define the global and local coordinate systems
    global_coords = np.array([normalized_vectors[0], normalized_vectors[1], normalized_vectors[2]])
    local_coords = np.array([normalized_vectors[3], normalized_vectors[4], normalized_vectors[5]])

    # Calculate the transformation matrix from global to local coordinates
    transform_matrix = local_coords @ np.linalg.inv(global_coords)

    # Calculate the transformation matrix that maps the global origin to the new origin
    origin_transform_matrix = np.identity(4)
    origin_transform_matrix[:3, 3] = global_origin.np

    # Combine the transformation matrices
    combined_transform_matrix = transform_matrix @ origin_transform_matrix[:3, :3]

    # Transform the point from global to local coordinates
    point_local = combined_transform_matrix @ (point.np - global_origin.np)

    return Point(point_local[0], point_local[1], point_local[2])


def get_global_coordinate(point_local: Point,
                          plane: Plane,
                          origin_x: Vector = Vector(1, 0, 0),
                          origin_y: Vector = Vector(0, 1, 0), ):
    vectors = []

    destination_x = plane.x_vector
    destination_y = plane.y_vector

    global_origin = plane.origin

    origin_z = np.cross(origin_x.np, origin_y.np)
    destination_z = np.cross(destination_x.np, destination_y.np)
    vectors.append(origin_x.np)
    vectors.append(origin_y.np)
    vectors.append(origin_z)
    vectors.append(destination_x.np)
    vectors.append(destination_y.np)
    vectors.append(destination_z)

    normalized_vectors = []

    for vector in vectors:
        length = np.linalg.norm(vector)
        v_norm = vector / length

        normalized_vectors.append(v_norm)

    # Define the global and local coordinate systems
    global_coords = np.array([normalized_vectors[0], normalized_vectors[1], normalized_vectors[2]])
    local_coords = np.array([normalized_vectors[3], normalized_vectors[4], normalized_vectors[5]])

    # Calculate the transformation matrix from global to local coordinates
    transform_matrix = local_coords @ np.linalg.inv(global_coords)

    # Calculate the transformation matrix that maps the global origin to the new origin
    origin_transform_matrix = np.identity(4)
    origin_transform_matrix[:3, 3] = global_origin.np

    # Combine the transformation matrices
    combined_transform_matrix = transform_matrix @ origin_transform_matrix[:3, :3]

    # Calculate the inverse of the transformation matrix to go from local to global coordinates
    inv_transform_matrix = np.linalg.inv(combined_transform_matrix)

    # Transform the point from local to global coordinates
    point_global = inv_transform_matrix @ point_local.np + global_origin.np

    return Point(point_global[0], point_global[1], point_global[2])


def distance_to_zero(point):
    return math.sqrt(point.x ** 2 + point.y ** 2 + point.z ** 2)