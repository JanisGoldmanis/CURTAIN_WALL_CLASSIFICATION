import os
from .read_file import process_file
from .errors import verification
from .settings import settings
from . import flask_app
import time

"""
web - set to True for default use together with React
    - set to False to run in Python console for debug purposes
"""
web = True

cw_backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Check if necessary data folders exist, create them, if not
verification.check_data_folders(cw_backend_dir, settings)

if __name__ == '__main__':
    flask_app.set_current_directory(cw_backend_dir)
    process_file.set_current_directory(cw_backend_dir)
    if web:
        flask_app.app.run()
    else:
        start = time.time()
        # result = process_file.process_files("Sickla6.csv,SicklaOpenings3.csv")
        result = process_file.process_files("ParkCentral5.csv,ParkCentralOpenings.csv")
        print('Time spent:', time.time()-start)
