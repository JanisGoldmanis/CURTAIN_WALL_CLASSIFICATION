import os
import json
import csv
from itertools import zip_longest
import logging

# Set up logging configuration
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(message)s')


def get_type_count(option1_list):
    """
    option1_list = list of {name, description}
    :param option1_list:
    :return: dictionary with description, it's key and quantity
    """
    unique_entries = set()

    i = 1
    objects = {}

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
        result += opening["TYPE"]
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

    with open(output_folder + '\output_openings.csv', 'w', newline='') as file:

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

            logging.debug(f'No Location: {opening}')

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
        type = opening["TYPE"]
        if type not in type_count:
            type_count[type] = 1
        else:
            type_count[type] += 1
    else:
        for child in opening["CHILDREN"]:
            get_type_usage(child, type_count)


def get_option_descriptions(json_folder):
    file_names = get_file_names(json_folder)
    option_descriptions = []

    for i in range(len(file_names)):

        file_name = file_names[i]

        file_path = os.path.join(json_folder, file_name)

        opening_type_count = {}

        with open(file_path) as f:
            data = json.load(f)
        guid = data['GUID']

        delivery_number = data["DELIVERY_NUMBER"]

        opening_type_count = {}

        string_option2 = f"{data['HEIGHT']} x {data['WIDTH']}"

        string_option1 = ''
        i = 0
        for plane in data['PLANES']:
            i += 1
            string_option1 += f'P{i} '
            opening = plane['OPENING']

            get_type_usage(opening, opening_type_count)

            try:
                string_option1 += get_opening_string_option1(opening)
            except:
                print(f'There are problems with generating string option1 for {guid}')

        type_count_string = ''
        keys = opening_type_count.keys()
        for key in keys:
            if key == '':
                type_count_string += f'{opening_type_count[key]}{"-"} '
            else:
                type_count_string += f'{opening_type_count[key]}{key} '

        string_option1 = f'{type_count_string}{string_option1}'

        option_descriptions.append({"name": file_name, "option1": string_option1, "option2": string_option2,
                                    "delivery_number": delivery_number})

    return option_descriptions


def generate_output_grouping(option_descriptions, types, output_folder):
    with open(output_folder + '\output_grouping.csv', 'w', newline='', encoding='UTF8') as file:
        writer = csv.writer(file, delimiter=';')

        writer.writerow(["NAME", "Option 1", "Option 1 description", "Option 2", "Option 2 Description"])
        for item in option_descriptions:
            name = item["delivery_number"]
            description = item["option1"]
            type = f'Group {types[description]["key"]}'

            size_description = item["option2"]
            size_type = types[description]["size_list"][size_description]

            size_group = f'Group {types[description]["key"]}-{size_type}'

            row = [name, type, description, size_group, size_description]
            writer.writerow(row)


def generate_output_group_statistics(output_folder, types):
    with open(output_folder + '\group_statistics.csv', 'w', newline='', encoding='UTF8') as file:
        writer = csv.writer(file, delimiter=';')

        writer.writerow(["TYPE", "TOTAL COUNT", "SPLIT INTO"])

        keys = types.keys()

        for key in keys:
            object = types[key]
            size_count = [key, object["count"]]

            sizes = object["size_count"].keys()

            for size in sizes:
                size_count.append(object["size_count"][size])

            writer.writerow(size_count)


def analyze_jsons(output_folder, json_folder):
    # Generate output openings csv report, information used for Engineers
    generate_output_openings(output_folder, json_folder)

    option_descriptions = get_option_descriptions(json_folder)

    types = get_type_count(option_descriptions)

    # Generate output element grouping - information for factory
    generate_output_grouping(option_descriptions, types, output_folder)

    generate_output_group_statistics(output_folder, types)

    return types
