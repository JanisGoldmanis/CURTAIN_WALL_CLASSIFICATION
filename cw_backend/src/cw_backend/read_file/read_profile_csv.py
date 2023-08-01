import csv
from ..classes.element_representation import profile as profile_module, element as element_module
from ..errors import error_handling, verification
from .. import settings

error_log_file = error_handling.errors

indexes = {"profile_index": 0,
           "length_index": 1,
           "start_x_index": 2,
           "start_y_index": 3,
           "start_z_index": 4,
           "end_x_index": 5,
           "end_y_index": 6,
           "end_z_index": 7,
           "part_guid_index": 8,
           "assembly_guid_index": 9,
           "delivery_number": 10
           }

left_to_right_direction = settings.settings["left_to_right_direction"]


def read_csv(file_path):
    try:
        error_log_file.pop("CSV PARSING")
    except KeyError:
        pass
    # Method will go over each row of csv file.
    # First it looks at guid, if such element has already been created.
    # Second if, necessary it creates new element object and then adds profile to necessary element.
    previous_element_guid = set()
    elements = []

    with open(file_path, encoding='UTF-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')

        # Skip first row (csv header)
        next(reader)

        for row in reader:

            try:

                assembly_guid = row[indexes["assembly_guid_index"]]

                # For AILE, "profiles" are beam elements AND cross-sections of those elements.
                new_profile = row[indexes["profile_index"]]

                length = float(row[indexes["length_index"]].replace(" ", ""))
                guid = row[indexes["part_guid_index"]]
                start_x = float(row[indexes["start_x_index"]].replace(" ", ""))
                start_y = float(row[indexes["start_y_index"]].replace(" ", ""))
                start_z = float(row[indexes["start_z_index"]].replace(" ", ""))
                end_x = float(row[indexes["end_x_index"]].replace(" ", ""))
                end_y = float(row[indexes["end_y_index"]].replace(" ", ""))
                end_z = float(row[indexes["end_z_index"]].replace(" ", ""))
                delivery_number = row[indexes["delivery_number"]]
            except IndexError:
                error_log_file["CSV PARSING"] = {"ERROR": "Index Error",
                                                 "ROW": row,
                                                 "CAUSE": "Most likely missing required columns, "
                                                          "please see example CSV"}
                return False

            if assembly_guid not in previous_element_guid:
                previous_element_guid.add(assembly_guid)
                elements.append(element_module.Element(assembly_guid))

            for single_element in elements:
                if single_element.guid == assembly_guid:
                    new_profile = profile_module.Profile(new_profile, length, guid,
                                                         start_x, start_y, start_z,
                                                         end_x, end_y, end_z,
                                                         delivery_number)

                    if not left_to_right_direction:
                        new_profile.start, new_profile.end = new_profile.end, new_profile.start

                    single_element.profiles.append(new_profile)

    elements, bad_elements = verification.valid_or_invalid_elements(elements)

    if len(bad_elements) > 0:
        print('\nBad elements:')
        for single_element in bad_elements:
            print(single_element.guid)
        print()

    # After creation of element objects, profiles are split into element planes (necessary for corner elements)

    print(f'Read {len(elements)} elements from file')
    print('Working...')
    i = 0
    for single_element in elements:

        element_module.assign_delivery_number(single_element)

        i += 1
        # print(i, element.guid)
        single_element.generate_planes()
        for plane in single_element.element_planes:
            plane.generate_size()
    print('Planes Generated')
    print('Working...')

    return elements
