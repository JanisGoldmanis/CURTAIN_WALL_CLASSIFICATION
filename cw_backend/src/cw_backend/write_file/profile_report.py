import os
import json
import csv
import traceback


def get_file_names(directory_path):
    """
    USED!
    Gets all files in a directory
    :param directory_path:
    :return:
    """
    filename_list = []
    for filename in os.listdir(directory_path):
        if os.path.isfile(os.path.join(directory_path, filename)):
            filename_list.append(filename)
    return filename_list


def generate_profile_report(output_folder, elements):
    print('Generating profile report')
    report_file_path = os.path.join(output_folder, "profile_report.csv")

    result = []

    for element in elements:
        for element_plane in element.element_planes:
            opening = element_plane.opening
            local_result = {}
            success = get_profile_openings(opening, local_result)
            if not success:
                continue

            left = opening.left
            right = opening.right
            top = opening.top
            bottom = opening.bottom
            frame_profiles = [left, right, top, bottom]

            all_profiles = element_plane.all_profiles
            if len(local_result) != len(all_profiles):
                continue

            for profile in element_plane.all_profiles:

                type_string = get_type_string(profile, local_result[profile.guid])

                if profile not in frame_profiles:
                    name = 'T'+profile.direction+'-'+type_string

                elif profile == left:
                    name = 'FL' + '-' + type_string
                elif profile == right:
                    name = 'FR' + '-' + type_string
                elif profile == top:
                    name = 'FT' + '-' + type_string
                elif profile == bottom:
                    name = 'FB' + '-' + type_string
                else:
                    name = 'error'

                result.append([profile.guid, name])

    with open(report_file_path, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['GUID', 'NAME'])
        for line in result:
            writer.writerow(line)


def get_profile_openings(opening, result):
    if len(opening.children) == 0:
        if opening.type is None:
            return False
        profiles = [opening.bottom, opening.top, opening.left, opening.right]
        for profile in profiles:
            if profile != '' and profile is not None:
                guid = profile.guid

                if guid not in result:
                    result[guid] = []
                result[guid].append(opening)
        return True
    else:
        for child in opening.children:
            success = get_profile_openings(child, result)
            if not success:
                return False
        return True


def get_type_string(profile, opening_list):
    direction = profile.direction
    midpoint = profile.middle_point
    lists = []

    if direction == 'V':
        left = []
        right = []

        for opening in opening_list:
            if opening.origin.x < midpoint.x:
                left.append(opening)
            else:
                right.append(opening)
        left.sort(key=lambda item: item.origin.y)
        left.reverse()
        right.sort(key=lambda item: item.origin.y)
        right.reverse()
        if len(left) > 0:
            lists.append(left)
        if len(right) > 0:
            lists.append(right)

    if direction == 'H':
        top = []
        bottom = []

        for opening in opening_list:
            if opening.origin.y < midpoint.y:
                bottom.append(opening)
            else:
                top.append(opening)
        bottom.sort(key=lambda item: item.origin.x)
        top.sort(key=lambda item: item.origin.x)
        if len(top) > 0:
            lists.append(top)
        if len(bottom) > 0:
            lists.append(bottom)

    strings = []
    for list in lists:
        type_string = ''.join([opening.type for opening in list])
        strings.append(type_string)
    return '-'.join(strings)





