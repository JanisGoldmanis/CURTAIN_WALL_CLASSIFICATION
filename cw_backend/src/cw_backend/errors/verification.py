from . import create_missing_data_folders


def correct_amount_of_beams(element):
    if len(element.profiles) < 4:
        return False
    return True


def any_profile_is_vertical(element):
    for profile in element.profiles:
        if abs(profile.start.z - profile.end.z) > 50:
            return True
    return False


def valid_or_invalid_elements(elements):
    element_list_copy = elements[:]
    bad_elements = []
    used_delivery_numbers = set()

    for element in element_list_copy:
        profile_count = correct_amount_of_beams(element)
        vertical = any_profile_is_vertical(element)

        if not profile_count or not vertical or element.delivery_number in used_delivery_numbers:
            elements.remove(element)
            bad_elements.append(element)

    return elements, bad_elements


def check_data_folders(backend_directory, settings):
    create_missing_data_folders.create_missing_data_folders(backend_directory, settings)
