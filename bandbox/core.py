import os
import sys
from collections import UserDict

import bandbox


class Tree(UserDict):
    def __new__(cls, sep='/', show_file_counts=True):
        cls.sep = sep
        cls.show_file_counts = show_file_counts
        return super().__new__(cls)

    def insert(self, dir_entry: os.DirEntry, prefix: str = ''):
        path_list = dir_entry.path[len(prefix):].strip(self.sep).split(self.sep)
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
            if '_files' not in insertion_point:
                insertion_point['_files'] = [path_list[-1]]
            else:
                insertion_point['_files'] += [path_list[-1]]
        else:
            insertion_point[path_list[-1]] = dict()

    @staticmethod
    def file_counts(file_list):
        file_counts = dict()
        for file_ in file_list:
            file_match = bandbox.FILE_EXTENSION_CAPTURE_CRE.match(file_)
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
    def get_empty_dirs(tree_dict, parent=""):
        empty_dirs = list()
        for dir_entry, children in tree_dict.items():
            if len(children) == 0:  # terminal empty folder
                empty_dirs.append(f"{parent}{dir_entry}")
            if len(children) == 1:  # non-terminal folder with files only
                if "_files" not in children and not isinstance(children, list):
                    empty_dirs.append(f"{parent}{dir_entry}")
            if isinstance(children, (dict, Tree)):
                empty_dirs += Tree.get_empty_dirs(children, parent=f"{parent}{dir_entry}/")
        return empty_dirs

    def find_empty_directories(self, include_root=True) -> list:
        """Identify directories with no files"""
        empty_dirs = Tree.get_empty_dirs(self)
        if include_root:
            return empty_dirs
        return empty_dirs[1:]

    @staticmethod
    def get_obvious_folders(tree_dict, parent=""):
        obvious = list()
        for dir_entry, children in tree_dict.items():
            if bandbox.OBVIOUS_FILES_CRE.match(dir_entry):
                obvious.append(f"{parent}{dir_entry}")
            if isinstance(children, (dict, Tree)):
                obvious += Tree.get_obvious_folders(children, parent=f"{parent}{dir_entry}/")
        return obvious

    def find_obvious_folders(self, include_root=True) -> list:
        obvious_dirs = Tree.get_obvious_folders(self)
        return obvious_dirs

    @staticmethod
    def get_excessive_files(tree_dict, parent=""):
        excess = list()
        for dir_entry, children in tree_dict.items():
            if '_files' in tree_dict:
                if len(tree_dict['_files']) > bandbox.MAX_FILES:
                    excess.append(f"{parent}{dir_entry}")
            if isinstance(children, (dict, Tree)):
                excess += Tree.get_excessive_files(children, parent=f"{parent}{dir_entry}/")
        return excess

    def find_excessive_files_per_directory(self) -> list:
        excess = Tree.get_excessive_files(self)
        return excess

    @staticmethod
    def get_long_names(tree_dict, parent=""):
        long_names = list()
        for dir_entry, children in tree_dict.items():
            if len(dir_entry) > bandbox.MAX_NAME_LENGTH:
                long_names.append(f"{parent}{dir_entry}")
            if isinstance(children, (dict, Tree)):
                long_names += Tree.get_long_names(children, parent=f"{parent}{dir_entry}/")
        return long_names

    def find_long_names(self) -> list:
        long_names = Tree.get_long_names(self)
        return long_names
