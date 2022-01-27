# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
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
FILE_CRE = re.compile(r"^.*\..*$", re.IGNORECASE)


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
                string += f" {self._recursive_string(extraction_point=extraction_point[key], indent=indent)}\n"
                indent = indent[:-1]
            else:
                string += f"{indent}└── [{len(value)} file(s)]"
                indent = indent[:-1]
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
    try:
        path = sys.argv[1]
    except IndexError:
        path = "~/PycharmProjects/oil/world_availability/10310"
    try:
        prefix = sys.argv[2]
    except IndexError:
        prefix = "/Users/pkorir/PycharmProjects/oil/world_availability/"
    data = glob.glob(str(pathlib.Path(os.path.expanduser(path)) / "**"), recursive=True)
    print(data)
    tree = Tree.from_data(data, prefix=prefix)
    print(tree.data)
    print(json.dumps(tree.data, indent=4))
    print(tree)
    return os.EX_OK


if __name__ == '__main__':
    sys.exit(main())
