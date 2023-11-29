from ..other import geometry
from . import profile, element_plane


# element_representation objects are first created as "dumb" objects only containing GUID, and added profiles to the
# profiles list Afterwards, profiles are sorted into "dumb" element planes Lastly element planes are split into
# openings
class Element:
    def __init__(self, guid):
        self.guid = guid
        self.profiles = []
        self.element_planes = []
        self.plane_count = 0
        self.delivery_number = ''
        self.physical_openings = []
        self.error = ''

    def __str__(self):
        return f'{self.guid} | {len(self.profiles)}'

    def generate_planes(self):
        bottom_profiles = profile.find_bottom_beams(self.profiles)

        if len(bottom_profiles) > 1:
            profile.sort_bottom_profiles(bottom_profiles)
            profile.adjust_profile_lengths(bottom_profiles)

        profiles_by_planes = element_plane.sort_profiles_by_planes(bottom_profiles, self.profiles)

        # Create element plane "dumb" objects
        for _ in range(len(profiles_by_planes)):
            bottom_profile = bottom_profiles.pop(0)
            all_profiles_on_plane = profiles_by_planes.pop(0)
            if len(all_profiles_on_plane) == 0:
                return False
            self.element_planes.append(element_plane.ElementPlane(bottom_profile, all_profiles_on_plane))

        # Orient coordinates to plane local coordinate system
        for single_plane in self.element_planes:
            target_plane = single_plane.plane
            for single_profile in single_plane.all_profiles:
                single_profile.start = geometry.get_local_coordinate(single_profile.start, target_plane)
                single_profile.end = geometry.get_local_coordinate(single_profile.end, target_plane)
                single_profile.direction = single_profile.get_direction_local()
                single_profile.orient_points()

        self.plane_count = len(self.element_planes)
        return True


def assign_delivery_number(element):
    if element.profiles[0].delivery_number != '':
        element.delivery_number = element.profiles[0].delivery_number
    else:
        element.delivery_number = element.guid


def get_element_dimensions(element):
    height = 0
    width = 0

    for plane in element.element_planes:
        height = plane.height
        width += plane.width

    return {"HEIGHT": height, "WIDTH": width}


def get_opening_level(opening, level):
    if len(opening.children) == 0:
        return max(opening.level, level)
    else:
        child_levels = [level]
        for child in opening.children:
            child_levels.append(get_opening_level(child, level))
        return max(child_levels)


def get_element_max_level(element):
    level = 0

    for plane in element.element_planes:
        opening = plane.opening
        level = get_opening_level(opening, level)

    return level
