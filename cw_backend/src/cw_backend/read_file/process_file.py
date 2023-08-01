import os
from . import point_cloud, read_profile_csv
from ..classes.element_representation import opening
from ..errors import error_handling
from ..settings import settings
from ..write_file import write_json, analyze_element_difference, analyze_jsons, draw_svg

results = {"Errors": error_handling.errors}  # Store the results

settings = settings.settings

current_dir = ''


def set_current_directory(current_directory):
    global current_dir
    current_dir = current_directory


def process_files(filename):
    global current_dir

    # Input
    opening_report = os.path.join(current_dir, 'node_input', 'OpeningData.csv')

    # profile_report = os.path.join(current_dir, 'Aile_Element_Classification', 'node_input', filename)
    profile_report = os.path.join(current_dir, 'data', settings["node_input"], filename)

    # Output
    json_folder = os.path.join(current_dir, 'data', settings["json_folder"])

    output_folder = os.path.join(current_dir, 'data', settings["output_folder"])

    svg_folder = os.path.join(current_dir, 'data', settings["svg_folder"])
    write_jsons = settings["write_jsons"]
    draw_element = settings["draw_element"]
    analyze_json = settings["analyze_json"]

    difference_folder = os.path.join(current_dir, 'data', settings["difference_results"])

    assign_opening_type = settings["assign_opening_type"]

    # Group profiles by GUID's into distinct element objects
    elements = read_profile_csv.read_csv(profile_report)

    if not elements:
        return False

    if assign_opening_type:
        # Get point cloud from Opening Report
        point_cloud_array = point_cloud.get_point_cloud_array(opening_report)

    print('Generating openings, writing')
    print('Working...')

    # Call the function to delete the files

    write_json.delete_files_in_folder(json_folder)
    write_json.delete_files_in_folder(svg_folder)

    for element in elements:
        # try:
        for plane in element.element_planes:
            plane.generate_openings()
        for plane in element.element_planes:
            if assign_opening_type:
                opening.assign_opening_type(plane.opening, plane.plane, point_cloud_array)
        if draw_element:
            draw_svg.draw_element(element, svg_folder)
        if write_jsons:
            write_json.write_json(element, json_folder)
        # except:
        #     print('Problem', element.guid)
    if analyze_json:
        print('Analyzing JSONs')
        print('Working')
        analyze_jsons.analyze_jsons(output_folder, json_folder)

        if settings["analyze_differences"]:
            analyze_element_difference.generate_report_of_similar_but_different_openings(json_folder,
                                                                                         output_folder,
                                                                                         difference_folder)

        # results[filename] = result  # Store the result using the filename as the key
    return True
