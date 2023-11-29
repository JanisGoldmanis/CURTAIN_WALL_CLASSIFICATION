import os
import json
import csv
from .. import settings
from . import opening_report
from . import profile_report


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


def generate_element_dimensions(output_folder, elements):

    output_openings_file_path = os.path.join(output_folder, "element_dimensions.csv")

    print('Generating element dimension report')

    with open(output_openings_file_path, 'w', newline='') as file:

        writer = csv.writer(file, delimiter=';')
        writer.writerow(['DELIVERY NUMBER', 'HEIGHT', 'WIDTH', 'AREA'])

        for element in elements:
            name = element.delivery_number

            width = 0
            height = 0
            for element_plane in element.element_planes:
                width += element_plane.width
                height = max(height, element_plane.height)

            row = [name, height, width, round(height*width/(10**6),2)]

            writer.writerow(row)