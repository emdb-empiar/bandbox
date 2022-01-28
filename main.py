# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import argparse
import glob
import json
import os
import pathlib
import re
import sys
from collections import UserDict

import requests

FILE_EXTENSIONS = "jpg|jpeg|mrc|mrcs"
FILE_CRE = re.compile(rf"^([^.]*\.[^.]*|.*\.({FILE_EXTENSIONS}))$", re.IGNORECASE)
FILE_EXTENSION_CAPTURE_CRE = re.compile(rf".*\.(?P<ext>({FILE_EXTENSIONS}))$", re.IGNORECASE)


def get_gist_data():
    """Read up to date data from the Github gist"""
    response = requests.get(
        "https://gist.githubusercontent.com/paulkorir/5b71f57f7a29391f130e53c24a2db3fb/raw/da9142bb59479c278d1291165f1b416cf22030f8/bandbox.json")
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


class Tree(UserDict):
    def __new__(cls, sep='/', show_file_counts=True):
        cls.sep = sep
        cls.show_file_counts = show_file_counts
        return super().__new__(cls)

    def insert(self, path: str, prefix: str):
        path_list = path.lstrip(prefix).strip(self.sep).split(self.sep)
        insertion_point = self.data
        for element in path_list:
            if element not in insertion_point:
                if FILE_CRE.match(element):  # a file
                    if 'files' not in insertion_point:
                        insertion_point['files'] = [element]
                    else:
                        insertion_point['files'] += [element]
                else:
                    insertion_point[element] = dict()
                    insertion_point = insertion_point[element]
            else:
                if FILE_CRE.match(element):  # a file
                    if 'files' not in insertion_point:
                        insertion_point['files'] = [element]
                    else:
                        insertion_point['files'] += [element]
                else:  # a directory
                    insertion_point = insertion_point[element]

    @staticmethod
    def file_counts(file_list):
        file_counts = dict()
        for file_ in file_list:
            file_match = FILE_EXTENSION_CAPTURE_CRE.match(file_)
            if file_match:
                ext = file_match.group('ext')
                if ext not in file_counts:
                    file_counts[ext] = 1
                else:
                    file_counts[ext] += 1
            else:
                print(f"warning: file '{file_}' did not match any extension", file=sys.stderr)
        return file_counts

    def _recursive_string(self, extraction_point, indent=""):
        string = ""
        for key, value in extraction_point.items():
            if isinstance(value, dict):
                string += f"{indent}└── {key}\n"
                indent += "\t"
                string += f" {self._recursive_string(extraction_point=extraction_point[key], indent=indent)}"
                indent = indent[:-1]
            else:
                if len(value) == 1:
                    item = "file"
                else:
                    item = "files"
                if self.show_file_counts:
                    file_counts_str = ""
                    file_counts = self.file_counts(value)
                    for ext, count in file_counts.items():
                        file_counts_str += f"{ext}={count};"
                    string += f"{indent}└── [{len(value)} {item}: {file_counts_str}]\n"
                else:
                    string += f"{indent}└── [{len(value)} {item}]\n"

        return string

    def __str__(self):
        """Print as tree"""
        string = self._recursive_string(self.data)
        return string

    @classmethod
    def from_data(cls, data, prefix="", show_file_counts=True):
        tree = cls()
        tree.show_file_counts = show_file_counts
        for t in data:
            tree.insert(t, prefix=prefix)
        return tree


def main():
    parser = argparse.ArgumentParser(prog='bandbox', description="Diagnose disorganised data file/folders")
    parser.add_argument('path', default='.', help="path to diagnose [default: '.']")
    parser.add_argument('-p', '--prefix', default='', help="prefix to exclude [default: '']")
    parser.add_argument('-d', '--display-paths', default=False, action='store_true',
                        help="display all the directories found [default: False]")
    parser.add_argument('-i', '--input-data', help="input data from a file")
    parser.add_argument('--hide-file-counts', default=True, action='store_false',
                        help="display file counts [default: True]")
    args = parser.parse_args()
    get_gist_data()
    if args.input_data:
        with open(args.input_data) as f:
            data = f.read().strip().split(', ')
    else:
        data = glob.glob(str(pathlib.Path(os.path.expanduser(args.path)) / "**"), recursive=True)
    tree = Tree.from_data(data, prefix=args.prefix, show_file_counts=args.hide_file_counts)
    if args.display_paths:
        print(data)
        print(tree.data)
        print(json.dumps(tree.data, indent=4))
    try:
        print(tree)
    except BrokenPipeError:
        pass
    return os.EX_OK


if __name__ == '__main__':
    sys.exit(main())
