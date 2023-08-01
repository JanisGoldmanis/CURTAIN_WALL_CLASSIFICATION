import os


def create_missing_data_folders(backend_dir, settings):
    node_input_path = settings["node_input"]
    output_path = settings["output_folder"]
    json_folder = settings["json_folder"]
    svg_folder = settings["svg_folder"]
    difference_folder = settings["difference_results"]

    folders = [node_input_path, output_path, json_folder, svg_folder, difference_folder]
    path = os.path.join(backend_dir, 'data')

    for folder in folders:
        folder_path = os.path.join(path, folder)

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f'Created {folder} folder')
