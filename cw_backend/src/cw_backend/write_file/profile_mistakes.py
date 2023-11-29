import os
import json
import csv


def generate_profile_mistakes(output_folder, profiles):

    output_openings_file_path = os.path.join(output_folder, "profile_anomalies.csv")

    print('Generating profile mistake report')

    result = {}

    for profile in profiles:
        cro_sec = profile.profile
        if cro_sec not in result:
            result[cro_sec] = {"count": 0, "sizes": {}}
        length = profile.length
        current_result_cro_sec = result[cro_sec]
        current_result_cro_sec["count"] += 1
        if length not in current_result_cro_sec["sizes"]:
            current_result_cro_sec["sizes"][length] = {"count": 0, "id": []}
        current_length = current_result_cro_sec["sizes"][length]
        current_length["count"] += 1
        current_length["id"].append(profile.guid)

    bad_situations = []

    for cro_sec in result:
        object = result[cro_sec]
        sizes = list(object['sizes'].keys())
        sizes.sort()

        bad_sizes = []

        for i in range(len(sizes)-1):
            if sizes[i+1] - sizes[i] < 5:
                if sizes[i] not in bad_sizes:
                    bad_sizes.append(sizes[i])
                if sizes[i+1] not in bad_sizes:
                    bad_sizes.append(sizes[i+1])

        for size in bad_sizes:
            bad_situations.append({"profile": cro_sec, "size": size, "count": object['sizes'][size]['count']})





        # print(sizes)




    with open(output_openings_file_path, 'w', newline='') as file:

        writer = csv.writer(file, delimiter=';')
        writer.writerow(['PROFILE', 'SIZE', 'COUNT'])

        for object in bad_situations:
            profile = object['profile']
            size = object['size']
            count = object['count']

            row = [profile, size, count]

            writer.writerow(row)

    return True, result