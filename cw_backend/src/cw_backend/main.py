from .read_file import process_file
from .errors import verification
from .settings import settings
import os
import flask_app

"""
web - set to True for default use together with React
    - set to False to run in Python console for debug purposes
"""
web = True

# Retrieve the directory for main.py and the move 1 folder up to retrieve cw_backend path
cw_backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Check if necessary data folders exist, create them, if not
verification.check_data_folders(cw_backend_dir, settings)

if __name__ == '__main__':
    flask_app.set_current_directory(cw_backend_dir)
    process_file.set_current_directory(cw_backend_dir)
    if web:
        flask_app.app.run()
    else:
        result = process_file.process_files("Geely2.csv")
        print('Finished')
