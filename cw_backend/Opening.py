import Geometry
import copy
import Profile

import Settings


tolerance = Settings.settings["profile_end_tolerance"]


class Opening:
    def __init__(self, height, width, origin: Geometry.Point, profiles, plane, level):

        self.top = ''
        self.right = ''
        self.bottom = ''
        self.left = ''

        self.height = height
        self.width = width

        self.profiles_inside = ''
        self.origin = origin

        self.center = Geometry.Point(int(origin.x + width / 2), int(origin.y + height / 2), int(origin.z))
        self.type = ''

        self.children = []
        self.split_direction = ''
        self.profiles_all = profiles
        self.level = level

        self.plane = plane
        self.local_opening_plane = copy.deepcopy(plane)

        self.adjust_plane_origin()

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

    inside_profiles_copy = inside_profiles[:]
    crossing_profiles = []

    for profile in inside_profiles_copy:
        if profile.direction == 'H':
            if (abs(profile.start.x - father.origin.x) < tolerance and abs(
                    profile.end.x - father.origin.x - width) < tolerance) or (
                    abs(profile.end.x - father.origin.x) < tolerance and abs(
                    profile.start.x - father.origin.x - width) < tolerance):
                crossing_profiles.append(profile)
                inside_profiles.remove(profile)
        if profile.direction == 'V':
            if (abs(profile.start.y - father.origin.y) < tolerance and abs(
                    profile.end.y - father.origin.y - height) < tolerance) or (
                    abs(profile.end.y - father.origin.y) < tolerance and abs(
                    profile.start.y - father.origin.y - height) < tolerance):
                crossing_profiles.append(profile)
                inside_profiles.remove(profile)

    return crossing_profiles


def recursion_split_openings(father: Opening, inside_profiles, level):
    if len(inside_profiles) == 0:
        return True

    plane = father.plane
    width = father.width
    height = father.height

    # Get a list which profiles are fully crossing the father opening - splitting the father and creating new openings
    crossing_profiles = get_crossing_profiles(inside_profiles, father)

    if len(crossing_profiles) > 0:

        if crossing_profiles[0].direction == 'V':
            # All crossing profiles should have the same direction

            father.split_direction = 'V'
            sorted_profiles = sorted(crossing_profiles, key=lambda p: p.middle_point.x)

            top = father.top
            bottom = father.bottom
            sorted_profiles.insert(0, father.left)
            sorted_profiles.append(father.right)

            for _ in range(len(sorted_profiles) - 1):
                left = sorted_profiles.pop(0)
                right = sorted_profiles[0]
                all_profiles = [left, right, top, bottom]
                local_inside_profiles = []

                # If opening has all 4 perimeter profiles, more precise geometry information can be created
                if None not in all_profiles:
                    for profile in inside_profiles:
                        if left.middle_point.x < profile.middle_point.x < right.middle_point.x:
                            all_profiles.append(profile)
                            local_inside_profiles.append(profile)
                    local_height = top.middle_point.y - bottom.middle_point.y
                    local_width = right.middle_point.x - left.middle_point.x
                    local_origin = Geometry.Point(left.middle_point.x, bottom.middle_point.y, 0)
                    new_opening = Opening(local_height, local_width, local_origin, all_profiles, plane, level)
                    father.children.append(new_opening)
                    new_opening.top = top
                    new_opening.bottom = bottom
                    new_opening.left = left
                    new_opening.right = right
                    new_opening.level = level
                    new_opening.profiles_inside = local_inside_profiles

                    if len(local_inside_profiles) == 0:
                        continue
                    recursion_split_openings(new_opening, local_inside_profiles, level + 1)
                else:

                    # if Any perimeter profile is missing (opening has only 3 edge profiles, e.g. corner elements)
                    # Imprecise geometry information is created based on start/end handles instead of middle points.
                    for profile in inside_profiles:
                        x1 = father.origin.x
                        x2 = father.origin.x + width
                        if x1 < profile.middle_point.x < x2:
                            all_profiles.append(profile)
                            local_inside_profiles.append(profile)

                    if bottom is not None:
                        bottom: Profile
                        y1 = bottom.middle_point.y
                    else:
                        possible_y1 = []
                        if right is not None:
                            possible_y1.append(right.start.y)
                        if left is not None:
                            possible_y1.append(left.start.y)
                        y1 = max(possible_y1)

                    if top is not None:
                        top: Profile
                        y2 = top.middle_point.y
                    else:
                        possible_y2 = []
                        if right is not None:
                            possible_y2.append(right.end.y)
                        if left is not None:
                            possible_y2.append(left.end.y)
                        y2 = min(possible_y2)
                    local_height = y2 - y1

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

                    local_width = x2 - x1
                    local_origin = Geometry.Point(x1, y1, 0)
                    new_opening = Opening(local_height, local_width, local_origin, all_profiles, plane, level)
                    father.children.append(new_opening)
                    new_opening.top = top
                    new_opening.bottom = bottom
                    new_opening.left = left
                    new_opening.right = right
                    new_opening.level = level
                    new_opening.profiles_inside = local_inside_profiles

                    if len(local_inside_profiles) == 0:
                        continue
                    recursion_split_openings(new_opening, local_inside_profiles, level + 1)

        if crossing_profiles[0].direction == 'H':
            father.split_direction = 'H'
            sorted_profiles = sorted(crossing_profiles, key=lambda p: p.middle_point.y)

            left = father.left
            right = father.right
            sorted_profiles.insert(0, father.bottom)
            sorted_profiles.append(father.top)

            for _ in range(len(sorted_profiles) - 1):
                bottom = sorted_profiles.pop(0)
                top = sorted_profiles[0]
                all_profiles = [left, right, top, bottom]
                local_inside_profiles = []

                if None not in all_profiles:

                    for profile in inside_profiles:

                        if bottom.middle_point.y < profile.middle_point.y < top.middle_point.y:
                            all_profiles.append(profile)
                            local_inside_profiles.append(profile)
                    local_height = top.middle_point.y - bottom.middle_point.y
                    local_width = right.middle_point.x - left.middle_point.x
                    local_origin = Geometry.Point(left.middle_point.x, bottom.middle_point.y, 0)
                    new_opening = Opening(local_height, local_width, local_origin, all_profiles, plane, level)
                    father.children.append(new_opening)
                    new_opening.top = top
                    new_opening.bottom = bottom
                    new_opening.left = left
                    new_opening.right = right
                    new_opening.level = level
                    new_opening.profiles_inside = local_inside_profiles

                    if len(local_inside_profiles) == 0:
                        continue
                    recursion_split_openings(new_opening, local_inside_profiles, level + 1)
                else:
                    for profile in inside_profiles:
                        y1 = father.origin.y
                        y2 = father.origin.y + height
                        if y1 < profile.middle_point.x < y2:
                            all_profiles.append(profile)
                            local_inside_profiles.append(profile)

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
                    local_height = y2 - y1

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

                    local_width = x2 - x1
                    local_origin = Geometry.Point(x1, y1, 0)
                    new_opening = Opening(local_height, local_width, local_origin, all_profiles, plane, level)
                    father.children.append(new_opening)
                    new_opening.top = top
                    new_opening.bottom = bottom
                    new_opening.left = left
                    new_opening.right = right
                    new_opening.level = level
                    new_opening.profiles_inside = local_inside_profiles

                    if len(local_inside_profiles) == 0:
                        continue
                    recursion_split_openings(new_opening, local_inside_profiles, level + 1)

    # else:
        # print(f"There are inside profiles that aren't crossing anything!\n{father}")

def assign_opening_type(opening, plane, point_cloud_array):
    if len(opening.children) == 0:
        opening_center_global = Geometry.get_global_coordinate(opening.center, plane)

        index = int(round(Geometry.distance_to_zero(opening_center_global) / 1000, 0))
        # print(index)
        try:
            point_cloud = point_cloud_array[index - 1] + point_cloud_array[index] + point_cloud_array[index + 1]
        except Exception as e:
            print(e)

        if len(point_cloud) == 0:
            opening.type = None
        else:
            closest_point = point_cloud[0]
            distance = Geometry.distance_2pt(opening_center_global, closest_point)

            for point in point_cloud:
                temp_distance = Geometry.distance_2pt(point, opening_center_global)
                if distance >= temp_distance:
                    closest_point = point
                    distance = temp_distance

            if Geometry.distance_2pt(closest_point, opening_center_global) < 400:
                opening.type = closest_point.name
            else:
                opening.type = "-"

    for opening_child in opening.children:
        assign_opening_type(opening_child, plane, point_cloud_array)
