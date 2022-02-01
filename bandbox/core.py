import os
import sys
from collections import UserDict

from bandbox.utils import FILE_EXTENSION_CAPTURE_CRE


class Tree(UserDict):
    def __new__(cls, sep='/', show_file_counts=True):
        cls.sep = sep
        cls.show_file_counts = show_file_counts
        return super().__new__(cls)

    def insert(self, dir_entry: os.DirEntry, prefix: str = ''):
        path_list = dir_entry.path.removeprefix(prefix).strip(self.sep).split(self.sep)
        # first, deal with folders
        insertion_point = self.data
        for element in path_list[:-1]:
            if element not in insertion_point:
                insertion_point[element] = dict()
                insertion_point = insertion_point[element]
            else:
                insertion_point = insertion_point[element]
        # last item
        if dir_entry.is_file():
            if 'files' not in insertion_point:
                insertion_point['files'] = [path_list[-1]]
            else:
                insertion_point['files'] += [path_list[-1]]
        else:
            insertion_point[path_list[-1]] = dict()

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

    @staticmethod
    def get_empty_dirs(tree_dict):
        empty_dirs = list()
        for dir_entry, children in tree_dict.items():
            if len(children) == 0: # terminal empty folder
                empty_dirs.append(dir_entry)
            if len(children) == 1: # non-terminal folder with files only
                if "files" not in children and not isinstance(children, list):
                    empty_dirs.append(dir_entry)
            if isinstance(children, (dict, Tree)):
                empty_dirs += Tree.get_empty_dirs(children)
        return empty_dirs

    def find_empty_directories(self, include_root=True) -> list:
        """Identify directories with no files"""
        empty_dirs = Tree.get_empty_dirs(self)
        if include_root:
            return empty_dirs
        return empty_dirs[1:]
