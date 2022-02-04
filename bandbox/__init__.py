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
DATE_RE = [
    # 12/31/2000 or 31/12/2000
    rf"^.*\d{{2}}[{DATE_INFIX_CHARS}]*\d{{2}}[{DATE_INFIX_CHARS}]*\d{{4}}.*$",
    # 2000[]12[]31 or 2000[]31[]12
    rf"^.*\d{{4}}[{DATE_INFIX_CHARS}]*\d{{2}}[{DATE_INFIX_CHARS}]*\d{{2}}.*$",
    # 31[]12[]00
    rf"^.*\d{{2}}[{DATE_INFIX_CHARS}]*\d{{2}}[{DATE_INFIX_CHARS}]*\d{{2}}.*$",
    # 31[]Dec[]2000
    rf"^.*\d{{2}}[{DATE_INFIX_CHARS}]*({MONTH_CHARS})[{DATE_INFIX_CHARS}]*\d{{4}}.*$",
    # Dec[]31[]2000
    rf"^.*\d{{4}}[{DATE_INFIX_CHARS}]*({MONTH_CHARS})[{DATE_INFIX_CHARS}]*\d{{2}}.*$",
]
DATE_CRE = list(map(lambda r: re.compile(r, re.IGNORECASE), DATE_RE))
ACCESSION_NAMES = "EMPIAR|EMDB"
ACCESSION_NAMES_CRE = re.compile(rf"^.*({ACCESSION_NAMES}).*$", re.IGNORECASE)
ODD_CHARS = "&?! ,"
ODD_CHARS_CRE = re.compile(rf".*[{ODD_CHARS}].*")
MAX_PERIODS_IN_NAME = 1
MAX_PERIODS_IN_NAME_CRE = re.compile(rf".*([.].*){{{MAX_PERIODS_IN_NAME + 1},}}.*")  # tricky!
EXTERNAL_REFS = "figure|supplementary"
EXTERNAL_REFS_CRE = re.compile(rf"^.*({EXTERNAL_REFS}).*$", re.IGNORECASE)


def get_gist_data(offline=False):
    """Read up to date data from the Github gist"""
    if offline:
        print(f"info: running in offline mode...", file=sys.stderr)
    else:
        response = requests.get(
            "https://gist.githubusercontent.com/paulkorir/5b71f57f7a29391f130e53c24a2db3fb/raw/bandbox.json"
        )
        if response.ok:
            print(f"info: successfully retrieved up-to-date data...", file=sys.stderr)
            global FILE_EXTENSIONS
            global FILE_CRE
            global FILE_EXTENSION_CAPTURE_CRE
            global OBVIOUS_FILES
            global OBVIOUS_FILES_CRE
            global MAX_FILES
            global MAX_NAME_LENGTH
            global DATE_INFIX_CHARS
            global MONTH_CHARS
            global DATE_RE
            global DATE_CRE
            global ACCESSION_NAMES
            global ACCESSION_NAMES_CRE
            global ODD_CHARS
            global ODD_CHARS_CRE
            global MAX_PERIODS_IN_NAME
            global MAX_PERIODS_IN_NAME_CRE
            global EXTERNAL_REFS
            global EXTERNAL_REFS_CRE
            assessment_data = response.json()
            FILE_EXTENSIONS = assessment_data['file_formats']
            FILE_CRE = re.compile(rf"^([^.]*\.[^.]*|.*\.({FILE_EXTENSIONS}))$", re.IGNORECASE)
            FILE_EXTENSION_CAPTURE_CRE = re.compile(rf".*\.(?P<ext>({FILE_EXTENSIONS}))$", re.IGNORECASE)
            # extend
            OBVIOUS_FILES += "|" + assessment_data["obvious_files"]
            OBVIOUS_FILES_CRE = re.compile(rf"^({OBVIOUS_FILES})$", re.IGNORECASE)
            MAX_FILES = assessment_data["max_files"]
            MAX_NAME_LENGTH = assessment_data["max_name_length"]
            DATE_INFIX_CHARS += assessment_data["date_infix_chars"]
            # extend
            MONTH_CHARS += "|" + assessment_data["month_chars"]
            DATE_RE = assessment_data["date_re"]
            # extend what we have
            DATE_CRE += list(map(lambda r: re.compile(r, re.IGNORECASE), DATE_RE))
            ACCESSION_NAMES = assessment_data["accession_names"]
            ACCESSION_NAMES_CRE = re.compile(rf"^.*({ACCESSION_NAMES}).*$", re.IGNORECASE)
            # extend
            ODD_CHARS = assessment_data["odd_chars"]
            ODD_CHARS_CRE = re.compile(rf".*[{ODD_CHARS}].*")
            MAX_PERIODS_IN_NAME = assessment_data["max_periods_in_name"]
            MAX_PERIODS_IN_NAME_CRE = re.compile(rf".*([.].*){{{MAX_PERIODS_IN_NAME + 1},}}.*")  # tricky!
            EXTERNAL_REFS = assessment_data["external_refs"]
            EXTERNAL_REFS_CRE = re.compile(rf"^.*({EXTERNAL_REFS}).*$", re.IGNORECASE)
        else:
            print(f"warning: unable to retrieve up-to-date data...", file=sys.stderr)
            print(f"warning: falling back to local data", file=sys.stderr)


get_gist_data()
