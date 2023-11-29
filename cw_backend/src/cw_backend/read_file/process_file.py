import os
import traceback

from . import point_cloud, read_profile_csv
from ..write_file import draw_svg, analyze_element_difference, analyze_jsons
from ..write_file import write_json
from ..classes.element_representation import opening
from .. import settings
from ..errors import error_handling
from ..errors import verification
from ..read_file import sort_files
from tqdm import tqdm
from ..write_file import error_log
from ..write_file import write_element_dimensions
from ..write_file import profile_report as profile_report_module
from ..write_file import profile_mistakes as profile_mistakes_module

results = {"Errors": error_handling.errors}

settings = settings.settings

current_dir = ''


def set_current_directory(current_directory):
    global current_dir
    current_dir = current_directory


def process_files(filenames):
    global current_dir

    output_folder = os.path.join(current_dir, 'data', settings["output_folder"])

    print('Deleting output files')
    write_json.delete_files_in_folder(output_folder)

    file_names = {"files": filenames.split(',')}

    try:
        files = sort_files.sort_files(file_names, current_dir)
    except Exception as e:
        print(f'Unhandled exception during sorting files:\n{e}')
        return False

    project_name = files["project_name"]

    if not verification.check_files(files):
        return False

    # Input
    opening_report = files["opening_file"]
    profile_report = files["profile_file"]

    # Output
    json_folder = os.path.join(current_dir, 'data', settings["json_folder"])
    svg_folder = os.path.join(current_dir, 'data', settings["svg_folder"])
    difference_folder = os.path.join(current_dir, 'data', settings["difference_results"])

    # Booleans
    write_jsons = settings["write_jsons"]
    draw_element = settings["draw_element"]
    analyze_json = settings["analyze_json"]
    assign_opening_type = settings["assign_opening_type"]

    # Group profiles by GUID's into distinct element objects
    elements, bad_elements, profiles = read_profile_csv.read_csv(profile_report)

    if not elements:
        return False

    opening_data_tree = {}
    if assign_opening_type:
        opening_data_tree = point_cloud.get_physical_opening_data_tree(opening_report, elements, bad_elements)

    print('Deleting json files')
    write_json.delete_files_in_folder(json_folder)
    print('Deleting svg files')
    write_json.delete_files_in_folder(svg_folder)

    for element in elements[:]:
        try:
            for plane in element.element_planes:
                plane.generate_openings()
        except Exception as e:
            elements.remove(element)
            bad_elements.append(element)
            element.error = f"Couldn't generate plane, {e}"

    for element in elements[:]:
        if not verification.left_or_right_side_as_single_profile(element):
            bad_elements.append(element)
            elements.remove(element)

    for element in elements[:]:
        if not verification.perimeter_profiles_are_necessary_length(element):
            bad_elements.append(element)
            elements.remove(element)

    print('Assigning opening type, creating svg, json')

    for element in tqdm(elements[:]):
        if assign_opening_type:
            for plane in element.element_planes:
                try:
                    opening.find_opening_types_for_plane(plane, opening_data_tree, element.physical_openings)
                except Exception as e:
                    traceback.print_exc()
                    bad_elements.append(element)
                    element.error = f"Couldn't determine opening types, {e}"
                    continue

        if draw_element:
            try:
                draw_svg.draw_element(element, svg_folder)
            except Exception as e:
                # elements.remove(element)
                traceback.print_exc()
                bad_elements.append(element)
                element.error = f"Couldn't draw svg, {e}"
                continue

        if write_jsons:
            try:
                write_json.write_json(element, json_folder)
            except Exception as e:
                traceback.print_exc()
                elements.remove(element)
                bad_elements.append(element)
                element.error = f"Couldn't write json, {e}"
                continue

    if analyze_json:
        try:
            analyze_jsons.analyze_jsons(output_folder, json_folder, project_name)
        except Exception as e:
            print(f'Unhandled exception during json analysis:\n{e}')
            return False

        if settings["analyze_differences"]:
            try:
                analyze_element_difference.generate_report_of_similar_but_different_openings(json_folder,
                                                                                             output_folder,
                                                                                             difference_folder)
            except Exception as e:
                print(f'Unhandled exception during difference analysis:\n{e}')
                return False

    write_element_dimensions.generate_element_dimensions(output_folder, elements)

    profile_mistakes_module.generate_profile_mistakes(output_folder, profiles)

    profile_report_module.generate_profile_report(output_folder, elements)

    if len(bad_elements) > 0:
        print(f'\n{len(bad_elements)} Bad Elements')
        error_log.write_error_log(bad_elements, output_folder)
        if analyze_json:
            analyze_jsons.add_bad_elements(bad_elements, output_folder, project_name)

    print('Finished')

    return True
