from . import analyze_jsons, write_json
from .. import settings

import os
import json


class AnalysisOpening:
    def __init__(self, height, width, parent, level, delivery_number):
        self.height = height
        self.width = width
        self.children = []
        self.parent = parent
        self.level = level
        self.delivery_number = delivery_number

    def preview(self, level):
        print(f'{"    " * level}{self.level} {self.height} x {self.width}')
        for child in self.children:
            child.preview(level + 1)


def create_opening_from_json(opening_data, parent, level, delivery_number):
    height = opening_data["HEIGHT"]
    width = opening_data["WIDTH"]

    opening = AnalysisOpening(height, width, parent, level, delivery_number)

    children = []
    for child in opening_data["CHILDREN"]:
        children.append(create_opening_from_json(child, opening, level + 1, delivery_number))
    opening.children = children

    return opening


def create_tree_object_from_opening(opening):
    height = opening.height
    width = opening.width

    tree_object = {"HEIGHT": {"MIN": height, "MAX": height}, "WIDTH": {"MIN": width, "MAX": width}, "CHILDREN": []}

    tree_object["DELIVERY_NUMBER"] = opening.delivery_number

    for child in opening.children:
        tree_object["CHILDREN"].append(create_tree_object_from_opening(child))

    return tree_object


def is_similar(tree_object_1, tree_object_2, tolerance):
    """
    :param tree_object_1: Main object
    :param tree_object_2: Object to compare against from Tree (includes count in main)
    :param tolerance:
    :return: True/False
    """
    height_1 = tree_object_1["HEIGHT"]["MIN"]
    height_2_min = tree_object_2["HEIGHT"]["MIN"]
    height_2_max = tree_object_2["HEIGHT"]["MAX"]

    if not height_2_min - tolerance < height_1 < height_2_max + tolerance:
        return False

    width_1 = tree_object_1["WIDTH"]["MIN"]
    width_2_min = tree_object_2["WIDTH"]["MIN"]
    width_2_max = tree_object_2["WIDTH"]["MAX"]

    if not width_2_min - tolerance < width_1 < width_2_max + tolerance:
        return False

    children_1 = tree_object_1["CHILDREN"]
    children_2 = tree_object_2["CHILDREN"]

    if len(children_1) != len(children_2):
        return False

    for i in range(len(children_1)):
        child_1 = children_1[i]
        child_2 = children_2[i]
        if not is_similar(child_1, child_2, tolerance):
            return False
    return True


def append_opening_to_tree_object(main_object, tree_object, add_first_level=False, min_tolerance=0.02):
    if add_first_level:
        tree_object["DELIVERY_NUMBER"].append(main_object["DELIVERY_NUMBER"])

    height_1 = main_object["HEIGHT"]["MIN"]
    height_2_min = tree_object["HEIGHT"]["MIN"]
    height_2_max = tree_object["HEIGHT"]["MAX"]

    height_keys = [x for x in tree_object["HEIGHT"].keys() if isinstance(x, float)]

    added = False

    for key in height_keys:
        if abs(height_1 - key) < min_tolerance:
            tree_object["HEIGHT"][key]["DELIVERY_NUMBER"].append(main_object["DELIVERY_NUMBER"])
            tree_object["HEIGHT"][key]["COUNT"] += 1
            added = True
            break
    if not added:
        tree_object["HEIGHT"][height_1] = {"DELIVERY_NUMBER": [main_object["DELIVERY_NUMBER"]], "COUNT": 1}

    if not added:
        if height_1 < height_2_min:
            tree_object["HEIGHT"]["MIN"] = height_1
        if height_1 > height_2_max:
            tree_object["HEIGHT"]["MAX"] = height_1

    width_1 = main_object["WIDTH"]["MIN"]
    width_2_min = tree_object["WIDTH"]["MIN"]
    width_2_max = tree_object["WIDTH"]["MAX"]

    width_keys = [x for x in tree_object["WIDTH"].keys() if isinstance(x, float)]

    added = False

    for key in width_keys:
        if abs(width_1 - key) < min_tolerance:
            tree_object["WIDTH"][key]["DELIVERY_NUMBER"].append(main_object["DELIVERY_NUMBER"])
            tree_object["WIDTH"][key]["COUNT"] += 1
            added = True
            break

    if not added:
        tree_object["WIDTH"][width_1] = {"DELIVERY_NUMBER": [main_object["DELIVERY_NUMBER"]], "COUNT": 1}

    if not added:
        if width_1 < width_2_min:
            tree_object["WIDTH"]["MIN"] = width_1
        if width_1 > width_2_max:
            tree_object["WIDTH"]["MAX"] = width_1

    children_1 = main_object["CHILDREN"]
    children_2 = tree_object["CHILDREN"]

    for i in range(len(children_1)):
        child_1 = children_1[i]
        child_2 = children_2[i]
        append_opening_to_tree_object(child_1, child_2, min_tolerance=min_tolerance)


def add_to_data_tree(data_tree, opening, tolerance, min_tolerance=0.02):
    added = False
    for tree_object in data_tree:
        if is_similar(opening, tree_object, tolerance):
            append_opening_to_tree_object(opening, tree_object, min_tolerance=min_tolerance, add_first_level=True)
            added = True
            break

    if not added:
        modify_opening_for_first_insertion_into_tree(opening, add_first_level=True)

        data_tree.append(opening)


def modify_opening_for_first_insertion_into_tree(opening, add_first_level=False):
    opening["HEIGHT"][opening["HEIGHT"]["MAX"]] = {"DELIVERY_NUMBER": [opening["DELIVERY_NUMBER"]], "COUNT": 1}
    opening["WIDTH"][opening["WIDTH"]["MAX"]] = {"DELIVERY_NUMBER": [opening["DELIVERY_NUMBER"]], "COUNT": 1}

    if add_first_level:
        opening["DELIVERY_NUMBER"] = [opening["DELIVERY_NUMBER"]]
    else:
        opening.pop("DELIVERY_NUMBER")

    for child in opening["CHILDREN"]:
        modify_opening_for_first_insertion_into_tree(child)


def data_tree_object_min_max_check(tree_object):
    height_min = tree_object["HEIGHT"]["MIN"]
    height_max = tree_object["HEIGHT"]["MAX"]

    width_min = tree_object["WIDTH"]["MIN"]
    width_max = tree_object["WIDTH"]["MAX"]

    if height_max != height_min:
        return False
    if width_max != width_min:
        return False

    for child in tree_object["CHILDREN"]:
        if not data_tree_object_min_max_check(child):
            return False

    return True


def change_min_max_to_single_value(tree_object, top_level_count=False):
    height_min = tree_object["HEIGHT"]["MIN"]
    height_max = tree_object["HEIGHT"]["MAX"]

    width_min = tree_object["WIDTH"]["MIN"]
    width_max = tree_object["WIDTH"]["MAX"]

    if height_min == height_max:
        tree_object["HEIGHT"] = height_min
    if width_min == width_max:
        tree_object["WIDTH"] = width_min

    for child in tree_object["CHILDREN"]:
        change_min_max_to_single_value(child)

    if len(tree_object["CHILDREN"]) == 0:
        tree_object.pop("CHILDREN")

    if top_level_count:
        tree_object["COUNT"] = len(tree_object["DELIVERY_NUMBER"])


def get_count_of_elements_to_adjust(data_tree_object, adjust_elements):
    keys = [x for x in data_tree_object["HEIGHT"].keys() if isinstance(x, float)]

    if len(keys) > 1:
        lists = [data_tree_object["HEIGHT"][key]["DELIVERY_NUMBER"] for key in keys]
        lists.sort(key=lambda x: len(x), reverse=True)

        for i in range(len(lists) - 1):
            for value in lists[i + 1]:
                adjust_elements.add(value)

    keys = [x for x in data_tree_object["WIDTH"].keys() if isinstance(x, float)]
    if len(keys) > 1:
        lists = [data_tree_object["WIDTH"][key]["DELIVERY_NUMBER"] for key in keys]
        lists.sort(key=lambda x: len(x), reverse=True)

        for i in range(len(lists) - 1):
            for value in lists[i + 1]:
                adjust_elements.add(value)

    for child in data_tree_object["CHILDREN"]:
        get_count_of_elements_to_adjust(child, adjust_elements)

    return True


def generate_report_of_similar_but_different_openings(json_folder, output_folder, difference_folder):
    file_names = analyze_jsons.get_file_names(json_folder)

    data_tree = []
    bad_tree_objects = []

    # mm
    tolerance = settings.settings["max_tolerance"]

    # mm
    min_tolerance = settings.settings["min_tolerance"]

    for i in range(len(file_names)):
        file_name = file_names[i]

        file_path = os.path.join(json_folder, file_name)

        with open(file_path) as f:
            data = json.load(f)

        # if "C" in data["DELIVERY_NUMBER"]:
        #     continue

        for plane in data["PLANES"]:
            opening_data = plane["OPENING"]
            delivery_number = data["DELIVERY_NUMBER"]
            opening = create_opening_from_json(opening_data, '', 0, delivery_number)

            # opening.preview(0)

            tree_object = create_tree_object_from_opening(opening)

            add_to_data_tree(data_tree, tree_object, tolerance, min_tolerance)

    for tree_object in data_tree:
        if not data_tree_object_min_max_check(tree_object):
            bad_tree_objects.append(tree_object)

    write_json.delete_files_in_folder(difference_folder)

    i = 1

    adjust_elements = set()

    for tree_object in data_tree:
        get_count_of_elements_to_adjust(tree_object, adjust_elements)

    print(f'Adjust {len(adjust_elements)} elements')

    for tree_object in bad_tree_objects:
        change_min_max_to_single_value(tree_object, top_level_count=True)

        json_data = json.dumps(tree_object, indent=4)

        file_path = f"{difference_folder}" + '/' + str(i) + '.json'

        with open(file_path, "w") as file:
            file.write(json_data)

        i += 1

# generate_report_of_similar_but_different_openings('Results', 'Output')
