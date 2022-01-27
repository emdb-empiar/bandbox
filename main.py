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

data = ['10003/', '10003/10003.xml', '10003/data', '10003/data/full_set', '10003/data/full_set/raw00001.dat',
        '10003/data/full_set/raw00002.dat', '10003/data/full_set/raw00005.dat', '10003/data/full_set/raw00006.dat',
        '10003/data/full_set/raw00007.dat', '10003/data/full_set/raw00008.dat', '10003/data/full_set/raw00009.dat',
        '10003/data/full_set/raw00010.dat', '10003/data/full_set/raw00012.dat', '10003/data/full_set/raw00013.dat',
        '10003/data/full_set/raw00014.dat', '10003/data/full_set/raw00015.dat', '10003/data/full_set/raw00016.dat', ]
FILE_CRE = re.compile(r"^([^.]*\.[^.]*|.*\.(jpg|jpeg|mrc|mrcs|tif|tiff))$", re.IGNORECASE)


class Tree(UserDict):
    def __new__(cls, sep='/'):
        cls.sep = sep
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
                string += f"{indent}└── [{len(value)} {item}]\n"
                # indent = indent[:-1]
        return string

    def __str__(self):
        """Print as tree"""
        string = self._recursive_string(self.data)
        return string

    @classmethod
    def from_data(cls, data, prefix=""):
        tree = cls()
        for t in data:
            tree.insert(t, prefix=prefix)
        return tree


def main():
    parser = argparse.ArgumentParser(prog='bandbox', description="Diagnose disorganised data file/folders")
    parser.add_argument('path', default='.', help="path to diagnose [default: '.']")
    parser.add_argument('-p', '--prefix', default='', help="prefix to exclude [default: '']")
    parser.add_argument('-d', '--display-paths', default=False, action='store_true', help="display all the directories found [default: False]")
    parser.add_argument('-i', '--input-data', help="input data from a file")
    args = parser.parse_args()
    if args.input_data:
        with open(args.input_data) as f:
            data = f.read().strip().split(', ')
    else:
        data = glob.glob(str(pathlib.Path(os.path.expanduser(args.path)) / "**"), recursive=True)
    tree = Tree.from_data(data, prefix=args.prefix)
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
