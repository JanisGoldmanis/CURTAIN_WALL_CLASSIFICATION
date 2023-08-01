from ..other import geometry


class Profile:
    def __init__(self, profile, length, guid, start_x, start_y, start_z, end_x, end_y, end_z, delivery_number):
        self.profile = profile
        self.length = length
        self.guid = guid
        self.start = geometry.Point(start_x, start_y, start_z)
        self.global_start = geometry.Point(start_x, start_y, start_z)
        self.end = geometry.Point(end_x, end_y, end_z)
        self.global_end = geometry.Point(end_x, end_y, end_z)
        self.direction = self.get_direction()
        self.delivery_number = delivery_number

    def orient_points(self):
        """
        After generating planes and local point coordinates have been translated to the plane coordinate system
        profile start and end points are checked to ensure, directions are left -> right and down -> up
        """
        if self.direction == 'V':
            if self.start.y > self.end.y:
                self.start, self.end = self.end, self.start
        if self.direction == 'H':
            if self.start.x > self.end.x:
                self.start, self.end = self.end, self.start

    def __str__(self):
        return f'|{self.direction:>4} | {self.start} | {self.end} | {self.guid} {self.length}'

    def get_direction(self):
        """
        This method is used on initialization for global coordinates
        """
        if abs(self.global_start.z - self.global_end.z) < 1:
            return 'H'
        if abs(self.global_start.x - self.global_end.x) < 1 and abs(self.global_start.y - self.global_end.y) < 1:
            return 'V'
        return "Diagonal"

    def get_direction_local(self):
        """
        This method is used after profiles have been orientated to element plane local coordinates
        """
        if abs(self.start.y - self.end.y) < 1:
            return 'H'
        if abs(self.start.x - self.end.x) < 1:
            return 'V'
        return "Diagonal"

    @property
    def middle_point(self):
        middle_x = self.start.x + (self.end.x - self.start.x) / 2
        middle_y = self.start.y + (self.end.y - self.start.y) / 2
        middle_z = self.start.z + (self.end.z - self.start.z) / 2
        return geometry.Point(middle_x, middle_y, middle_z)


def find_h_profile_at_y_pos(y_pos, all_profiles, tolerance=50):
    """
    Method is used for finding profiles at the top and bottom of opening
    """
    for profile in all_profiles:
        if profile.direction == 'H':
            if abs(profile.middle_point.y - y_pos) < tolerance:
                return profile
    return None


def find_v_profile_at_x_pos(x_pos, all_profiles, tolerance=50):
    """
    Method is used for finding profiles at the left and right side of opening
    """
    for profile in all_profiles:
        if profile.direction == 'V':
            if abs(profile.middle_point.x - x_pos) < tolerance:
                return profile
    return None


def find_bottom_beams(profiles):
    bottom_profiles = [profiles[0]]

    for profile in profiles[1:]:

        if profile.middle_point.z < bottom_profiles[0].middle_point.z - 100:
            bottom_profiles = [profile]

        elif bottom_profiles[0].middle_point.z - 100 < profile.middle_point.z < bottom_profiles[0].middle_point.z + 100:
            bottom_profiles.append(profile)
    return bottom_profiles


def sort_bottom_profiles(bottom_profiles):
    if len(bottom_profiles) > 1:
        first = bottom_profiles[0]
        second = bottom_profiles[1]

        distance1 = geometry.distance_2pt(first.end, second.start)
        distance2 = geometry.distance_2pt(second.end, first.start)

        if distance2 < distance1:
            bottom_profiles.reverse()
