import os
import sys
from collections import UserDict

from bandbox.utils import FILE_EXTENSION_CAPTURE_CRE


def scandir_recursive(path: str) -> os.DirEntry:
    """Recursive scanning of directories

    Returns a generator of os.DirEntry objects. We only distinguish between directories and everything else
    """
    with os.scandir(path) as dir_entries:
        for dir_entry in dir_entries:
            if dir_entry.is_dir():
                if os.listdir(dir_entry.path):  # non-empty directory
                    yield dir_entry  # the directory...
                    yield from scandir_recursive(dir_entry.path)  # plus its content
                else:
                    yield dir_entry  # the directory only

            else:
                yield dir_entry


class Tree(UserDict):
    def __new__(cls, sep='/', indent='', show_file_counts=True):
        cls.sep = sep
        cls.show_file_counts = show_file_counts
        cls.indent = indent
        return super().__new__(cls)

    def get_path(self, path, prefix: str = ''):
        """Given the path, return the subtree"""
        # a/b/c/d
        path_list = path.lstrip(prefix).strip(self.sep).split(self.sep)
        extraction_point = self
        for element in path_list[:-1]:
            extraction_point = extraction_point[element]
        return extraction_point[path_list[-1]]

    def set_path(self, path, prefix: str = ''):
        path_list = path.lstrip(prefix).strip(self.sep).split(self.sep)
        # a/b/c/d
        insertion_point = self
        for i, element in enumerate(path_list[:-2]):
            insertion_point[element] = Tree()
            insertion_point[element].indent = "\t" * i
            insertion_point = insertion_point[element]
        insertion_point[path_list[-2]] = path_list[-1]

    def insert(self, dir_entry: os.DirEntry, prefix: str = ''):
        """Insert some path with the prefix to exclude into the tree"""
        path_list = dir_entry.path.lstrip(prefix).strip(self.sep).split(self.sep)
        # if dir_entry.is_dir():
        #     self = {
        #         'type': 'directory',
        #         'name': dir_entry.name,
        #         'contents': []
        #     }
        # elif dir_entry.is_file():
        #     pass

        for element in path_list:
            if element not in self:
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
        # for element in path_list:
        #     if element not in insertion_point:
        #         if FILE_CRE.match(element):  # a file
        #             if 'files' not in insertion_point:
        #                 insertion_point['files'] = [element]
        #             else:
        #                 insertion_point['files'] += [element]
        #         else:
        #             insertion_point[element] = dict()
        #             insertion_point = insertion_point[element]
        #     else:
        #         if FILE_CRE.match(element):  # a file
        #             if 'files' not in insertion_point:
        #                 insertion_point['files'] = [element]
        #             else:
        #                 insertion_point['files'] += [element]
        #         else:  # a directory
        #             insertion_point = insertion_point[element]

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
