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
DATE_INFIX_CHARS = r"-:/."  # must start with '-'
MONTH_CHARS = (r"jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|"
               r"january|february|march|april|may|june|july|august|september|october|november|december")
DATE_CRE = [
    # 12/31/2000 or 31/12/2000
    re.compile(rf"^.*\d{{2}}[{DATE_INFIX_CHARS}]*\d{{2}}[{DATE_INFIX_CHARS}]*\d{{4}}.*$", re.IGNORECASE),
    # 2000[]12[]31 or 2000[]31[]12
    re.compile(rf"^.*\d{{4}}[{DATE_INFIX_CHARS}]*\d{{2}}[{DATE_INFIX_CHARS}]*\d{{2}}.*$", re.IGNORECASE),
    # 31[]12[]00
    re.compile(rf"^.*\d{{2}}[{DATE_INFIX_CHARS}]*\d{{2}}[{DATE_INFIX_CHARS}]*\d{{2}}.*$", re.IGNORECASE),
    # 31[]Dec[]2000
    re.compile(rf"^.*\d{{2}}[{DATE_INFIX_CHARS}]*({MONTH_CHARS})[{DATE_INFIX_CHARS}]*\d{{4}}.*$", re.IGNORECASE),
    # Dec[]31[]2000
    re.compile(rf"^.*\d{{4}}[{DATE_INFIX_CHARS}]*({MONTH_CHARS})[{DATE_INFIX_CHARS}]*\d{{2}}.*$", re.IGNORECASE)
    # re.compile(rf"^.*.*$", re.IGNORECASE)
]


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
