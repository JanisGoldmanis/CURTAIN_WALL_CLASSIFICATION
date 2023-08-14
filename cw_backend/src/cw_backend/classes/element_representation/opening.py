import copy
import numpy as np

from ..other import geometry
from ... import settings

tolerance = settings.settings["profile_end_tolerance"]


class Opening:
    def __init__(self, height, width, origin: geometry.Point, profiles, plane, level):
        self.top = ''
        self.right = ''
        self.bottom = ''
        self.left = ''

        self.height = height
        self.width = width

        self.profiles_inside = ''
        self.origin = origin

        self.center = geometry.Point(int(origin.x + width / 2), int(origin.y + height / 2), int(origin.z))
        self.type = ''

        self.children = []
        self.split_direction = ''
        self.profiles_all = profiles
        self.level = level

        self.plane = plane
        self.local_opening_plane = copy.deepcopy(plane)

        self.adjust_plane_origin()

        self.guid = ''
        self.name = ''
        self.assembly_guid = ''

    def __str__(self):
        return f'Level: {self.level}\n' \
               f'Local plane origin: {self.origin} | Height: {self.height} | Width: {self.width}\n' \
               f'Top {self.top}\n' \
               f'Bottom {self.bottom}\n' \
               f'Right {self.right}\n' \
               f'Left {self.left}\n' \
               f'Beams inside: {len(self.profiles_inside)}'

    def adjust_plane_origin(self):
        origin = self.origin

        x_direction = origin.x  # Distance to move in X direction
        y_direction = origin.y

        plane = self.local_opening_plane

        x_vector = plane.x_vector
        x_x_vector = x_vector.x
        y_x_vector = x_vector.y
        z_x_vector = x_vector.z

        total = (x_x_vector ** 2 + y_x_vector ** 2 + z_x_vector ** 2) ** 0.5

        x_x_vector /= total
        y_x_vector /= total
        z_x_vector /= total

        plane.origin.x += x_x_vector * x_direction
        plane.origin.y += y_x_vector * x_direction
        plane.origin.z += z_x_vector * x_direction

        y_vector = plane.y_vector
        x_y_vector = y_vector.x
        y_y_vector = y_vector.y
        z_y_vector = y_vector.z

        total = (x_y_vector ** 2 + y_y_vector ** 2 + z_y_vector ** 2) ** 0.5

        x_y_vector /= total
        y_y_vector /= total
        z_y_vector /= total

        plane.origin.x += x_y_vector * y_direction
        plane.origin.y += y_y_vector * y_direction
        plane.origin.z += z_y_vector * y_direction


def get_crossing_profiles(inside_profiles, father: Opening):
    width = father.width
    height = father.height

    crossing_profiles = []
    other_profiles = []

    for inside_profile in inside_profiles:
        if inside_profile.direction == 'H':
            if (abs(inside_profile.start.x - father.origin.x) < tolerance and abs(
                    inside_profile.end.x - father.origin.x - width) < tolerance) or (
                    abs(inside_profile.end.x - father.origin.x) < tolerance and abs(
                    inside_profile.start.x - father.origin.x - width) < tolerance):

                crossing_profiles.append(inside_profile)

            else:
                other_profiles.append(inside_profile)

        if inside_profile.direction == 'V':
            if (abs(inside_profile.start.y - father.origin.y) < tolerance and abs(
                    inside_profile.end.y - father.origin.y - height) < tolerance) or (
                    abs(inside_profile.end.y - father.origin.y) < tolerance and abs(
                    inside_profile.start.y - father.origin.y - height) < tolerance):

                crossing_profiles.append(inside_profile)

            else:
                other_profiles.append(inside_profile)

    return crossing_profiles, other_profiles


def get_imperfect_v_split_coordinates(top, bottom, left, right):
    if bottom is not None:
        y1 = bottom.middle_point.y
    else:
        possible_y1 = []
        if right is not None:
            possible_y1.append(right.start.y)
        if left is not None:
            possible_y1.append(left.start.y)
        y1 = max(possible_y1)

    if top is not None:
        y2 = top.middle_point.y
    else:
        possible_y2 = []
        if right is not None:
            possible_y2.append(right.end.y)
        if left is not None:
            possible_y2.append(left.end.y)
        y2 = min(possible_y2)

    if left is not None:
        x1 = left.middle_point.x
    else:
        possible_x1 = []
        if top is not None:
            possible_x1.append(top.start.x)
        if bottom is not None:
            possible_x1.append(bottom.start.x)
        x1 = max(possible_x1)

    if right is not None:
        x2 = right.middle_point.x
    else:
        possible_x2 = []
        if top is not None:
            possible_x2.append(top.end.x)
        if bottom is not None:
            possible_x2.append(bottom.end.x)
        x2 = min(possible_x2)

    return {"x1": x1, "x2": x2, "y1": y1, "y2": y2}


def get_imperfect_h_split_coordinates(top, bottom, left, right):
    if bottom is not None:
        y1 = bottom.middle_point.y
    else:
        possible_y1 = []
        if right is not None:
            possible_y1.append(right.start.y)
        if left is not None:
            possible_y1.append(left.start.y)
        y1 = max(possible_y1)

    if top is not None:
        y2 = top.middle_point.y
    else:
        possible_y2 = []
        if right is not None:
            possible_y2.append(right.end.y)
        if left is not None:
            possible_y2.append(left.end.y)
        y2 = min(possible_y2)

    if left is not None:
        x1 = left.middle_point.x
    else:
        possible_x1 = []
        if top is not None:
            possible_x1.append(top.start.x)
        if bottom is not None:
            possible_x1.append(bottom.start.x)
        x1 = max(possible_x1)

    if right is not None:
        x2 = right.middle_point.x
    else:
        possible_x2 = []
        if top is not None:
            possible_x2.append(top.end.x)
        if bottom is not None:
            possible_x2.append(bottom.end.x)
        x2 = min(possible_x2)

    return {"x1": x1, "x2": x2, "y1": y1, "y2": y2}


def add_perimeter_profiles_to_new_opening(new_opening, top, bottom, right, left, level, local_inside_profiles):
    new_opening.top = top
    new_opening.bottom = bottom
    new_opening.left = left
    new_opening.right = right
    new_opening.level = level
    new_opening.profiles_inside = local_inside_profiles


def recursion_split_openings(father: Opening, inside_profiles, level):
    # if there are no profiles inside the opening, no further splitting necessary
    if len(inside_profiles) == 0:
        return True

    plane = father.plane

    # Get a list which profiles are fully crossing the father opening - splitting the father and creating new openings
    crossing_profiles, non_crossing_profiles = get_crossing_profiles(inside_profiles, father)

    if len(crossing_profiles) > 0:

        if crossing_profiles[0].direction == 'V':
            # All crossing profiles should have the same direction

            father.split_direction = 'V'
            sorted_crossing_profiles = sorted(crossing_profiles, key=lambda p: p.middle_point.x)

            top = father.top
            bottom = father.bottom
            sorted_crossing_profiles.insert(0, father.left)
            sorted_crossing_profiles.append(father.right)

            for _ in range(len(sorted_crossing_profiles) - 1):
                left = sorted_crossing_profiles.pop(0)
                right = sorted_crossing_profiles[0]
                all_profiles = [left, right, top, bottom]
                local_inside_profiles = []

                # If opening has all 4 perimeter profiles, more precise geometry information can be created
                if None not in all_profiles:
                    left_coordinate = left.middle_point.x
                    right_coordinate = right.middle_point.x
                    for non_crossing_profile in non_crossing_profiles:
                        middle_coordinate = non_crossing_profile.middle_point.x
                        if left_coordinate < middle_coordinate < right_coordinate:
                            all_profiles.append(non_crossing_profile)
                            local_inside_profiles.append(non_crossing_profile)
                    local_height = top.middle_point.y - bottom.middle_point.y
                    local_width = right.middle_point.x - left.middle_point.x

                    local_origin = geometry.Point(left.middle_point.x, bottom.middle_point.y, 0)

                    new_opening = Opening(local_height, local_width, local_origin, all_profiles, plane, level)
                    father.children.append(new_opening)
                    add_perimeter_profiles_to_new_opening(new_opening,
                                                          top, bottom, right, left,
                                                          level,
                                                          local_inside_profiles)

                    if len(local_inside_profiles) == 0:
                        continue
                    recursion_split_openings(new_opening, local_inside_profiles, level + 1)
                else:

                    # if Any perimeter profile is missing (opening has only 3 edge profiles, e.g. corner elements)
                    # Imprecise geometry information is created based on start/end handles instead of middle points.
                    coordinates = get_imperfect_v_split_coordinates(top, bottom, left, right)

                    x1 = coordinates["x1"]
                    x2 = coordinates["x2"]
                    y1 = coordinates["y1"]
                    y2 = coordinates["y2"]

                    local_width = x2 - x1
                    local_height = y2 - y1

                    local_origin = geometry.Point(x1, y1, 0)

                    # Find profiles from non-crossing profiles that need to be added to the new opening
                    for non_crossing_profile in non_crossing_profiles:
                        middle_coordinate = non_crossing_profile.middle_point.x
                        if x1 < middle_coordinate < x2:
                            all_profiles.append(non_crossing_profile)
                            local_inside_profiles.append(non_crossing_profile)

                    new_opening = Opening(local_height, local_width, local_origin, all_profiles, plane, level)
                    father.children.append(new_opening)
                    add_perimeter_profiles_to_new_opening(new_opening,
                                                          top, bottom, right, left,
                                                          level,
                                                          local_inside_profiles)

                    if len(local_inside_profiles) == 0:
                        continue
                    recursion_split_openings(new_opening, local_inside_profiles, level + 1)

        if crossing_profiles[0].direction == 'H':
            father.split_direction = 'H'
            sorted_crossing_profiles = sorted(crossing_profiles, key=lambda p: p.middle_point.y)

            left = father.left
            right = father.right
            sorted_crossing_profiles.insert(0, father.bottom)
            sorted_crossing_profiles.append(father.top)

            for _ in range(len(sorted_crossing_profiles) - 1):
                bottom = sorted_crossing_profiles.pop(0)
                top = sorted_crossing_profiles[0]
                all_profiles = [left, right, top, bottom]
                local_inside_profiles = []

                if None not in all_profiles:
                    bottom_coordinate = bottom.middle_point.y
                    top_coordinate = top.middle_point.y
                    for non_crossing_profile in non_crossing_profiles:
                        middle_coordinate = non_crossing_profile.middle_point.y

                        if bottom_coordinate < middle_coordinate < top_coordinate:
                            all_profiles.append(non_crossing_profile)
                            local_inside_profiles.append(non_crossing_profile)
                    local_height = top.middle_point.y - bottom.middle_point.y
                    local_width = right.middle_point.x - left.middle_point.x
                    local_origin = geometry.Point(left.middle_point.x, bottom.middle_point.y, 0)
                    new_opening = Opening(local_height, local_width, local_origin, all_profiles, plane, level)
                    father.children.append(new_opening)
                    add_perimeter_profiles_to_new_opening(new_opening,
                                                          top, bottom, right, left,
                                                          level,
                                                          local_inside_profiles)

                    if len(local_inside_profiles) == 0:
                        continue
                    recursion_split_openings(new_opening, local_inside_profiles, level + 1)
                else:

                    coordinates = get_imperfect_h_split_coordinates(top, bottom, left, right)

                    x1 = coordinates["x1"]
                    x2 = coordinates["x2"]
                    y1 = coordinates["y1"]
                    y2 = coordinates["y2"]

                    local_width = x2 - x1
                    local_height = y2 - y1

                    for non_crossing_profile in non_crossing_profiles:
                        middle_coordinate = non_crossing_profile.middle_point.y
                        if y1 < middle_coordinate < y2:
                            all_profiles.append(non_crossing_profile)
                            local_inside_profiles.append(non_crossing_profile)

                    local_origin = geometry.Point(x1, y1, 0)
                    new_opening = Opening(local_height, local_width, local_origin, all_profiles, plane, level)
                    father.children.append(new_opening)
                    add_perimeter_profiles_to_new_opening(new_opening,
                                                          top, bottom, right, left,
                                                          level,
                                                          local_inside_profiles)

                    if len(local_inside_profiles) == 0:
                        continue
                    recursion_split_openings(new_opening, local_inside_profiles, level + 1)


def keep_openings_with_similar_orientation(plane, openings):
    x_vector = plane.x_vector.np
    y_vector = plane.y_vector.np
    z_vector_np = np.cross(x_vector, y_vector)

    similar_orientation_openings = []

    for opening in openings:
        plane2 = opening.plane
        x2_vector = plane2.x_vector.np
        y2_vector = plane2.y_vector.np
        z2_vector_np = np.cross(x2_vector, y2_vector)

        dot_product = np.dot(z_vector_np, z2_vector_np)

        magnitude_1 = np.linalg.norm(z_vector_np)
        magnitude_2 = np.linalg.norm(z2_vector_np)

        angle_rad = np.arccos(dot_product / (magnitude_1 * magnitude_2))

        angle_deg = abs(np.degrees(angle_rad))

        if 0 <= angle_deg <= 5 or 175 <= angle_deg <= 180:
            similar_orientation_openings.append(opening)
        else:
            continue
    return similar_orientation_openings


def get_ten_closest_openings(center, openings):
    try:
        openings = sorted(openings, key=lambda opening: geometry.distance_2pt(center, opening.center))
    except:
        test = ''
    distance = []

    for opening in openings:
        distance.append(geometry.distance_2pt(center, opening.center))
    return openings[:10]


def get_projected_onto_openings(center, openings):
    result_openings = []

    for opening in openings:
        local_point = geometry.get_local_coordinate(center, opening.plane)

        x = local_point.x
        y = local_point.y

        x_dimension = opening.height
        y_dimension = opening.width

        if 50 <= x <= x_dimension - 50 and 50 <= y <= y_dimension:
            result_openings.append(opening)

    return result_openings


def find_opening_types_for_plane(plane, physical_opening_data_tree, element_openings):
    cs_plane = plane.plane
    center_coordinate = plane.opening.center
    global_center_coordinate = geometry.get_global_coordinate(center_coordinate, cs_plane)

    opening = plane.opening

    rounded_distance = int(round(geometry.distance_to_zero(global_center_coordinate) / 1000, 0)) * 1000

    max_number = physical_opening_data_tree["max"]
    numbers = []
    for i in range(-3, 4):
        distance = rounded_distance + i * 1000
        if distance < 0:
            continue
        if distance > max_number:
            continue
        numbers.append(distance)

    nearby_openings = []

    for index in numbers:
        nearby_openings += physical_opening_data_tree[index]

    nearby_openings += element_openings

    same_orientation_nearby_openings = keep_openings_with_similar_orientation(cs_plane, nearby_openings)

    assign_opening_type(opening, cs_plane, same_orientation_nearby_openings)


def assign_opening_type(opening, plane, same_orientation_nearby_openings):
    if len(opening.children) == 0:
        opening_center_global = geometry.get_global_coordinate(opening.center, plane)

        ten_closest_openings_to_opening = get_ten_closest_openings(opening_center_global,
                                                                   same_orientation_nearby_openings)

        # Find within which openings you can project the point
        final_openings = get_projected_onto_openings(opening_center_global, ten_closest_openings_to_opening)

        if len(final_openings) > 0:
            opening_types = []
            for physical_opening in final_openings:
                opening_types.append(physical_opening.type)
            opening_type = '|'.join(opening_types)
            opening.type = opening_type
        else:
            opening.type = None

    for opening_child in opening.children:
        assign_opening_type(opening_child, plane, same_orientation_nearby_openings)
