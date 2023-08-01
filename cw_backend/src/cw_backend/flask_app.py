from flask import Flask, request, jsonify
from flask_cors import CORS
import traceback
from flask import send_from_directory
import os
import logging

from .read_file import process_file
import settings

app = Flask(__name__)
CORS(app)  # Enable CORS support

results = process_file.results  # Store the results

current_dir = ''


def set_current_directory(current_directory):
    global current_dir
    current_dir = current_directory


@app.route('/')
def custom_index():
    return "Custom message goes here"


@app.route('/favicon.ico')
def ignore_favicon_request():
    return '', 204  # Return an empty response with a 204 status code (No Content)


@app.route('/getResults')
def get_results():
    return jsonify(results)


@app.route('/api/upload', methods=['POST'])
def upload_file():
    try:
        # Access the uploaded file
        file = request.files['file']

        node_input = settings.settings['node_input']

        # Construct the relative path to the 'node_input' directory
        node_input_dir = os.path.join(current_dir, 'data', node_input)

        # Create the 'node_input' directory if it doesn't exist
        if not os.path.exists(node_input_dir):
            print(f'Created {node_input} directory')
            os.makedirs(node_input_dir)

        # Save the file to the 'node_input' directory
        file.save(os.path.join(node_input_dir, file.filename))

        # Prepare the response message
        response = {
            'result': 'File uploaded and saved successfully',
            'filename': file.filename,
        }

        # Return the response with a 200 status code (OK)
        return jsonify(response), 200

    except Exception as e:
        # Prepare the response message for upload failure
        response = {
            'result': 'File upload failed',
            'filename': file.filename,
        }
        logging.exception('Error during file upload:')
        traceback.print_exc()

        # Return the response with a 500 status code (Internal Server Error)
        return jsonify(response), 500


@app.route('/api/download/<folder>/<filename>', methods=['GET'])
def download_file(folder, filename):
    output_folder = os.path.join(current_dir, 'data', folder)
    return send_from_directory(output_folder, filename)


@app.route('/api/download/filelist', methods=['GET'])
def get_file_names():
    output_folder = settings.settings['output_folder']
    output_folder = os.path.join(current_dir, 'data', output_folder)

    filename_list = []
    for filename in os.listdir(output_folder):
        if os.path.isfile(os.path.join(output_folder, filename)):
            filename_list.append(filename)
    return {"file_list": filename_list}


@app.route('/api/delete/<folder>/<filename>', methods=['DELETE'])
def delete_file(folder, filename):
    path = os.path.join(current_dir, 'data', folder, filename)
    if os.path.isfile(path):
        try:
            os.remove(path)
            return "File deleted"
        except Exception as e:
            return "Error: File not deleted"
    else:
        return 'File not found'


@app.route('/api/process/<filename>', methods=['GET'])
def run_process_file(filename):
    response = {
        'filename': filename,
        'log': results
    }
    # Trigger the processing logic
    try:
        file_processed = process_file.process_files(filename)
        if file_processed:
            response['result'] = 'File Processed successfully'

        if not file_processed:
            response['result'] = 'Processing error'

    except Exception as e:
        response['result'] = 'Processing error'
        traceback.print_exc()
        return response

    return response


@app.route('/api/settings/<settings>', methods=['POST'])
def set_settings(settings):
    try:
        settings.settings = settings
        return True
    except Exception as e:
        traceback.print_exc()
        return False
