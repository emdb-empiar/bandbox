import re
import sys

import requests

FILE_EXTENSIONS = "jpg|jpeg|mrc|mrcs"
FILE_CRE = re.compile(rf"^([^.]*\.[^.]*|.*\.({FILE_EXTENSIONS}))$", re.IGNORECASE)
FILE_EXTENSION_CAPTURE_CRE = re.compile(rf".*\.(?P<ext>({FILE_EXTENSIONS}))$", re.IGNORECASE)
OBVIOUS_FILES = "file|files|data|folder|inner_folder"
OBVIOUS_FILES_CRE = re.compile(rf"^({OBVIOUS_FILES})$", re.IGNORECASE)
MAX_FILES = 5
MAX_NAME_LENGTH = 20


def get_gist_data():
    """Read up to date data from the Github gist"""
    response = requests.get(
        "https://gist.githubusercontent.com/paulkorir/5b71f57f7a29391f130e53c24a2db3fb/raw/bandbox.json"
    )
    if response.ok:
        print(f"info: successfully retrieved up-to-date data...", file=sys.stderr)
        global FILE_EXTENSIONS
        global FILE_CRE
        global FILE_EXTENSION_CAPTURE_CRE
        FILE_EXTENSIONS = response.json()['file_formats']
        FILE_CRE = re.compile(rf"^([^.]*\.[^.]*|.*\.({FILE_EXTENSIONS}))$", re.IGNORECASE)
        FILE_EXTENSION_CAPTURE_CRE = re.compile(rf".*\.(?P<ext>({FILE_EXTENSIONS}))$", re.IGNORECASE)
    else:
        print(f"warning: unable to retrieve up-to-date data...", file=sys.stderr)
        print(f"warning: falling back to local data", file=sys.stderr)


get_gist_data()
