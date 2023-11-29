import math

from . import create_missing_data_folders


def correct_amount_of_beams(element):
    if len(element.profiles) < 4:
        element.error = 'Less than 4 profiles in element'
        return False
    return True


def any_profile_is_vertical(element):
    for profile in element.profiles:
        if abs(profile.start.z - profile.end.z) > 50:
            return True
    element.error = 'No profile is vertical'
    return False


def are_vertical_profiles_in_the_same_xy(profile1, profile2):
    x1 = profile1.start.x
    x2 = profile2.start.x
    if abs(x1 - x2) < 50:
        return True
    return False


def left_or_right_side_as_single_profile(element):
    for plane in element.element_planes:
        profiles = plane.all_profiles
        opening = plane.opening
        left = opening.left
        right = opening.right

        for profile in profiles:
            if profile.direction == 'V':
                if left is not None:
                    if profile.guid != left.guid:
                        if are_vertical_profiles_in_the_same_xy(profile, left):
                            element.error = 'Split side profile'
                            return False
                if right is not None:
                    if profile.guid != right.guid:
                        if are_vertical_profiles_in_the_same_xy(profile, right):
                            element.error = 'Split side profile'
                            return False
    return True


def any_profile_is_diagonal(element):
    for profile in element.profiles:
        x_difference = abs(profile.start.x - profile.end.x)
        y_difference = abs(profile.start.y - profile.end.y)
        z_difference = abs(profile.start.z - profile.end.z)

        vertical_difference = z_difference
        horizontal_difference = math.sqrt(x_difference ** 2 + y_difference ** 2)

        if vertical_difference > 50 and horizontal_difference > 50:
            element.error = 'Diagonal profile in element'
            return True
    return False


def valid_or_invalid_elements(elements):
    element_list_copy = elements[:]
    bad_elements = []
    used_delivery_numbers = set()

    for element in element_list_copy:
        profile_count = correct_amount_of_beams(element)
        vertical = any_profile_is_vertical(element)
        diagonal = any_profile_is_diagonal(element)

        if not profile_count or not vertical or (element.delivery_number in used_delivery_numbers) or diagonal:
            elements.remove(element)
            bad_elements.append(element)

    return elements, bad_elements


def check_data_folders(backend_directory, settings):
    create_missing_data_folders.create_missing_data_folders(backend_directory, settings)


def check_files(files):

    if len(files["unknown_files"]) > 0:
        print('Bad report files')
        for file in files["unknown_files"]:
            print(file)
        return False

    if files["profile_file"] is None:
        print('No profile report file')
        return False

    return True


def perimeter_profiles_are_necessary_length(element):
    for element_plane in element.element_planes:
        opening = element_plane.opening
        left = opening.left
        right = opening.right
        top = opening.top
        bottom = opening.bottom

        height = opening.height
        width = opening.width

        if left is not None:
            if abs(height - left.length) > 100:
                element.error = 'Left profile is not sufficient length'
                return False
        if right is not None:
            if abs(height - right.length) > 100:
                element.error = 'Right profile is not sufficient length'
                return False
        if top is not None:
            if abs(width - top.length) > 100:
                element.error = 'Top profile is not sufficient length'
                return False
        if bottom is not None:
            if abs(width - bottom.length) > 100:
                element.error = 'Bottom profile is not sufficient length'
                return False
    return True
