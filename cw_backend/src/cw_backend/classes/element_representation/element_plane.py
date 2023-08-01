import math

from ..element_representation import profile, opening
from ..other import geometry
from ... import settings

tolerance = settings.settings["profile_end_tolerance"]


class ElementPlane:
    def __init__(self, bottom_beam, all_profiles):
        self.bottom_beam = bottom_beam
        self.all_profiles = all_profiles
        self.height = 0
        self.width = 0
        self.opening = ""
        self.plane = generate_plane_from_bottom_beam(bottom_beam, all_profiles)

    def __str__(self):
        return f'{self.height:>9} x {self.width:<9} Plane: {self.plane}'

    def generate_size(self):
        """
        Possible problem, currently size is generated from middle points.
        Possible cases with missing edge beams should be looked into.
        :return:
        """
        height = self.height
        width = self.width

        for beam in self.all_profiles:
            horizontal = max(beam.start.x, beam.end.x)
            vertical = max(beam.start.y, beam.end.y)

            if vertical > height:
                height = vertical
            if horizontal > width:
                width = horizontal

        self.height = height
        self.width = width

    def generate_openings(self):
        profiles = self.all_profiles[:]
        new_opening = opening.Opening(self.height, self.width, geometry.Point(0, 0, 0), self.all_profiles, self.plane,
                                      level=0)
        self.opening = new_opening
        new_opening.top = profile.find_h_profile_at_y_pos(self.height, profiles, tolerance)
        new_opening.bottom = profile.find_h_profile_at_y_pos(0, profiles, tolerance)
        new_opening.left = profile.find_v_profile_at_x_pos(0, profiles, tolerance)
        new_opening.right = profile.find_v_profile_at_x_pos(self.width, profiles, tolerance)

        if new_opening.top is not None:
            profiles.remove(new_opening.top)
        if new_opening.bottom is not None:
            profiles.remove(new_opening.bottom)
        if new_opening.left is not None:
            profiles.remove(new_opening.left)
        if new_opening.right is not None:
            profiles.remove(new_opening.right)

        new_opening.profiles_inside = profiles
        level = 1
        opening.recursion_split_openings(new_opening, profiles, level)


def generate_plane_from_bottom_beam(bottom_beam, all_profiles):
    start = bottom_beam.start
    end = bottom_beam.end
    origin = bottom_beam.start
    x0 = start.x
    y0 = start.y
    z0 = start.z
    x1 = end.x
    y1 = end.y
    z1 = end.z

    x_vector = geometry.Vector(x1 - x0, y1 - y0, z1 - z0)

    vertical_profile = find_most_vertical_profile(all_profiles)

    v_z_start = vertical_profile.start.z
    v_z_end = vertical_profile.end.z

    if v_z_start < v_z_end:
        v_start = vertical_profile.start
        v_end = vertical_profile.end
    else:
        v_start = vertical_profile.end
        v_end = vertical_profile.start

    v_x0 = v_start.x
    v_y0 = v_start.y
    v_z0 = v_start.z

    v_x1 = v_end.x
    v_y1 = v_end.y
    v_z1 = v_end.z

    y_vector = geometry.Vector(v_x1 - v_x0, v_y1 - v_y0, v_z1 - v_z0)

    return geometry.Plane(origin, x_vector, y_vector)


def find_most_vertical_profile(all_profiles):
    def get_ratio(beam):
        start = beam.start
        end = beam.end

        dif_x = end.x - start.x
        dif_y = end.y - start.y
        dif_z = abs(end.z - start.z)

        horizontal = math.sqrt(dif_x ** 2 + dif_y ** 2)
        if horizontal < 1:
            horizontal = 1
        vertical = dif_z
        profile_ratio = vertical / horizontal

        return profile_ratio

    vertical_profile = all_profiles[0]
    ratio = get_ratio(vertical_profile)

    for single_profile in all_profiles[1:]:
        temp_ratio = get_ratio(single_profile)

        if temp_ratio > ratio:
            ratio = temp_ratio
            vertical_profile = single_profile
    return vertical_profile


def sort_profiles_by_planes(bottom_profiles, all_profiles):
    result = []
    for _ in bottom_profiles:
        result.append([])
    for single_profile in all_profiles:
        if len(bottom_profiles) == 1:
            result[0].append(single_profile)
            continue

        if len(bottom_profiles) == 2:

            first = bottom_profiles[0]

            distance1, closest_point1 = geometry.distance_point_to_line(single_profile.middle_point, first)
            closest_point1 = geometry.Point(closest_point1[0], closest_point1[1], closest_point1[2])
            distance_to_start = geometry.distance_2pt(closest_point1, first.start)
            if distance_to_start < first.length + 10:
                within_first = True
            else:
                within_first = False

            second = bottom_profiles[1]

            distance2, closest_point2 = geometry.distance_point_to_line(single_profile.middle_point, second)
            closest_point2 = geometry.Point(closest_point2[0], closest_point2[1], closest_point2[2])
            distance_to_end = geometry.distance_2pt(closest_point2, second.end)

            if distance_to_end < second.length + 10:
                within_second = True
            else:
                within_second = False

            if within_first and not within_second:
                result[0].append(single_profile)
                continue

            elif not within_first and within_second:
                result[1].append(single_profile)
                continue

            else:
                if distance1 < distance2:
                    result[0].append(single_profile)
                    continue
                else:
                    result[1].append(single_profile)
    return result
