import os
import json
import csv
from .. import settings
from . import opening_report
from . import profile_report


def get_type_count(option1_list):
    """
    option1_list = list of {name, description}
    :param option1_list:
    :return: dictionary with description, it's key and quantity
    """
    unique_entries = set()

    i = 1
    objects = {}

    print('Generating types')

    for entry in option1_list:

        description = entry["option1"]

        size = entry["option2"]

        if description not in unique_entries:
            unique_entries.add(description)

            objects[description] = {"count": 0, "key": i, "size_list": [], "size_count": {}}
            i += 1

        objects[description]["count"] += 1
        if size not in objects[description]["size_list"]:
            objects[description]["size_list"].append(size)
            objects[description]["size_count"][size] = 0
        objects[description]["size_count"][size] += 1

    descriptions = objects.keys()
    for description in descriptions:
        sizes = objects[description]["size_list"]
        i = 1
        size_dict = {}

        for size in sizes:
            size_dict[size] = i
            i += 1
        objects[description]["size_list"] = size_dict

    return objects


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


def get_opening_string_option1(opening):
    result = '['

    split_direction = opening["SPLIT DIRECTION"]

    if len(split_direction) > 0:
        result += str(len(opening["CHILDREN"]))

    result += split_direction

    if len(opening["SPLIT DIRECTION"]) > 0:
        result += ' '

    for children in opening["CHILDREN"]:
        result += get_opening_string_option1(children)

    if len(opening["CHILDREN"]) == 0:
        opening_type = opening["TYPE"]
        if opening_type == None:
            opening_type = '-'
        result += opening_type
    result += '] '
    return result


def get_opening_size_data(opening):
    result = ''
    if len(opening['CHILDREN']) == 0:
        height = opening["HEIGHT"]
        width = opening["WIDTH"]

        result += f'|{height} x {width}|'
        return result
    else:
        for child in opening['CHILDREN']:
            result += get_opening_size_data(child)
        return result


def generate_output_openings(output_folder, json_folder):
    path = json_folder
    file_names = get_file_names(path)

    output_openings_file_path = os.path.join(output_folder, "output_openings.csv")

    print('Generating opening report')

    with open(output_openings_file_path, 'w', newline='') as file:

        writer = csv.writer(file, delimiter=';')
        writer.writerow(['TYPE', 'TOP', 'BOTTOM', 'LEFT', 'RIGHT', 'ORIGIN', 'X_VECTOR', 'Y_VECTOR', 'HEIGHT', 'WIDTH'])

        for i in range(len(file_names)):
            file_name = file_names[i]
            file_path = os.path.join(path, file_name)

            with open(file_path) as f:
                data = json.load(f)
            i = 0
            for plane in data['PLANES']:
                i += 1
                opening = plane['OPENING']
                row_array = []
                get_opening_row_array(opening, row_array)
                for row in row_array:
                    writer.writerow(row)


def get_opening_row_array(opening, result):
    if len(opening['CHILDREN']) == 0:
        try:
            top = opening['TOP']['GUID']
        except KeyError:
            top = 'None'

        try:
            bottom = opening['BOTTOM']['GUID']
        except KeyError:
            bottom = 'None'

        try:
            left = opening['LEFT']['GUID']
        except KeyError:
            left = 'None'

        try:
            right = opening['RIGHT']['GUID']
        except KeyError:
            right = 'None'

        try:
            type = opening['TYPE']
        except KeyError:
            type = 'None'
        try:
            location_dict = opening['LOCATION']
            origin = location_dict['ORIGIN']
            x_vector = location_dict['X_VECTOR']
            y_vector = location_dict['Y_VECTOR']
        except KeyError:

            origin = None
            x_vector = None
            y_vector = None

        height = opening['HEIGHT']
        width = opening['WIDTH']

        row = [type, top, bottom, left, right, origin, x_vector, y_vector, height, width]

        result.append(row)
    else:
        for child in opening['CHILDREN']:
            get_opening_row_array(child, result)


def get_type_usage(opening, type_count):
    if len(opening["CHILDREN"]) == 0:
        opening_type = opening["TYPE"]
        if opening_type is None:
            opening_type = '-'
        if opening_type not in type_count:
            type_count[opening_type] = 1
        else:
            type_count[opening_type] += 1
    else:
        for child in opening["CHILDREN"]:
            get_type_usage(child, type_count)


def get_option_descriptions(json_folder):
    rounding = settings.settings["rounding_precision_for_grouping"]
    file_names = get_file_names(json_folder)
    option_descriptions = []

    print('Generating descriptions')

    for i in range(len(file_names)):

        file_name = file_names[i]

        file_path = os.path.join(json_folder, file_name)

        with open(file_path) as f:
            data = json.load(f)
        guid = data['GUID']

        delivery_number = data["DELIVERY_NUMBER"]

        opening_type_count = {}

        string_option2 = f"{round(data['HEIGHT'], rounding)} x {round(data['WIDTH'], rounding)}"

        string_option1 = ''
        i = 0
        for plane in data['PLANES']:
            i += 1
            string_option1 += f'P{i} '
            opening = plane['OPENING']

            get_type_usage(opening, opening_type_count)

            # try:
            string_option1 += get_opening_string_option1(opening)
            # except:
            #     print(f'There are problems with generating string option1 for {guid}')

        type_count_string = ''
        keys = opening_type_count.keys()
        for key in keys:
            if key == '':
                type_count_string += f'{opening_type_count[key]}{"-"} '
            else:
                type_count_string += f'{opening_type_count[key]} x {key} '

        string_option1 = f'{type_count_string}{string_option1}'

        option_descriptions.append({"name": file_name, "option1": string_option1, "option2": string_option2,
                                    "delivery_number": delivery_number})

    return option_descriptions


def generate_output_grouping(option_descriptions, types, output_folder, project_name):
    output_grouping_file_path = os.path.join(output_folder, project_name + "_output_grouping.csv")
    with open(output_grouping_file_path, 'w', newline='', encoding='UTF8') as file:
        writer = csv.writer(file, delimiter=';')

        print('Generating element grouping report')

        writer.writerow(["NAME", "Opening List", "Option 1", "Option 1 description", "Option 2", "Option 2 Description"])
        for item in option_descriptions:
            name = item["delivery_number"]
            description = item["option1"]

            type = f'Group {types[description]["key"]}'

            size_description = item["option2"]
            size_type = types[description]["size_list"][size_description]

            size_group = f'Group {types[description]["key"]}-{size_type}'

            split_description = description.split('P1')
            opening_list = split_description.pop(0)
            description = 'P1' + split_description[0]

            row = [name, opening_list, type, description, size_group, size_description]
            writer.writerow(row)


def generate_output_group_statistics(output_folder, types):
    group_statistics_file_path = os.path.join(output_folder, "group_statistics.csv")
    with open(group_statistics_file_path, 'w', newline='', encoding='UTF8') as file:
        writer = csv.writer(file, delimiter=';')

        writer.writerow(["TYPE", "TOTAL COUNT", "SPLIT INTO"])

        keys = types.keys()

        print('Generating statistics')
        for key in keys:
            object = types[key]
            size_count = [f'Group {object["key"]} | {key}', object["count"]]

            sizes = object["size_count"].keys()

            for size in sizes:
                size_count.append(object["size_count"][size])

            writer.writerow(size_count)


def flatten_levels(json_object):
    result = []
    level_count = len(json_object[0].keys())

    for i in range(1, level_count + 1):
        level = []
        for plane in json_object:
            level += plane[str(i)]
        result.append(level)

    for i in range(len(result)):
        result[i] = '|'.join(result[i])

    return result


def add_element_to_result_tree(level_flat_information, branch, delivery_number):
    if len(level_flat_information) == 0:
        if "ELEMENTS" not in branch:
            branch["ELEMENTS"] = []
        branch["ELEMENTS"].append(delivery_number)
        branch["COUNT"] += 1
        return True

    key = level_flat_information.pop(0)

    if key not in branch:
        branch[key] = {"COUNT": 0}

    branch["COUNT"] += 1

    next_branch = branch[key]
    add_element_to_result_tree(level_flat_information, next_branch, delivery_number)


def get_type_tree(output_folder, json_folder):
    path = json_folder
    file_names = get_file_names(path)
    result_file_path = os.path.join(output_folder, "tree.something")

    result_tree = {"PLANE_COUNT": {}}

    for i in range(len(file_names)):
        file_name = file_names[i]
        file_path = os.path.join(path, file_name)

        with open(file_path) as f:
            data = json.load(f)

            plane_count = len(data["LEVELS"])
            delivery_number = data["DELIVERY_NUMBER"]

            flattened_information = flatten_levels(data["LEVELS"])

            if plane_count not in result_tree["PLANE_COUNT"]:
                result_tree["PLANE_COUNT"][plane_count] = {"COUNT": 0}

            current_branch = result_tree["PLANE_COUNT"][plane_count]

            add_element_to_result_tree(flattened_information, current_branch, delivery_number)

    json_data = json.dumps(result_tree, indent=4)
    # create a new file and write the JSON data to it
    file_name = "similarity" + '.json'
    file_path = os.path.join(output_folder, file_name)

    # draw_graph.draw_graph(result_tree)


    with open(file_path, "w") as file:
        file.write(json_data)

    return result_tree



def add_bad_elements(bad_elements, output_folder, project_name):
    file_path = os.path.join(output_folder, project_name + "_output_grouping.csv")

    with open(file_path, 'a', newline='', encoding='UTF8') as file:
        writer = csv.writer(file, delimiter=';')

        for element in bad_elements:
            delivery_number = element.delivery_number
            writer.writerow([delivery_number, element.error])


def analyze_jsons(output_folder, json_folder, project_name):
    # Generate output openings csv report, information used for Engineers
    generate_output_openings(output_folder, json_folder)

    option_descriptions = get_option_descriptions(json_folder)

    types = get_type_count(option_descriptions)

    # Generate output element grouping - information for factory
    generate_output_grouping(option_descriptions, types, output_folder, project_name)

    generate_output_group_statistics(output_folder, types)

    opening_report.generate_opening_report(output_folder, json_folder)

    similarity_tree = get_type_tree(output_folder, json_folder)

    return types
