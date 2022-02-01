import os
import pathlib
import re
import sys
import typing

import requests

FILE_EXTENSIONS = "jpg|jpeg|mrc|mrcs"
FILE_CRE = re.compile(rf"^([^.]*\.[^.]*|.*\.({FILE_EXTENSIONS}))$", re.IGNORECASE)
FILE_EXTENSION_CAPTURE_CRE = re.compile(rf".*\.(?P<ext>({FILE_EXTENSIONS}))$", re.IGNORECASE)


def get_gist_data():
    """Read up to date data from the Github gist"""
    response = requests.get(
        "https://gist.githubusercontent.com/paulkorir/5b71f57f7a29391f130e53c24a2db3fb/raw/bandbox.json")
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


def scandir_recursive(path: typing.Union[str, pathlib.Path], recursive=True,
                      exclude: typing.Union[None, list] = None) -> typing.Generator:
    """Recursively scan a directory

    Recursion can be switchef off
    """
    with os.scandir(path) as dir_entries:
        for dir_entry in dir_entries:
            if dir_entry.is_dir():
                if os.listdir(dir_entry.path):
                    yield dir_entry
                    if recursive:
                        yield from scandir_recursive(dir_entry.path)
                else:
                    yield dir_entry
            else:
                yield dir_entry
