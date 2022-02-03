import os
import re
import sys
from collections import UserDict

import bandbox
from bandbox.engines import RIGHT_COL_WIDTH, LEFT_COL_WIDTH


class Tree(UserDict):
    def __new__(cls, sep='/', show_file_counts=True):
        cls.sep = sep
        cls.show_file_counts = show_file_counts
        return super().__new__(cls)

    @classmethod
    def from_data(cls, data, prefix="", show_file_counts=True):
        tree = cls()
        tree.show_file_counts = show_file_counts
        for t in data:
            tree.insert(t, prefix=prefix)
        return tree

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
        extension_warnings = set()
        for file_ in file_list:
            file_match = bandbox.FILE_EXTENSION_CAPTURE_CRE.match(file_)
            if file_match:
                ext = file_match.group('ext')
                if ext not in file_counts:
                    file_counts[ext] = 1
                else:
                    file_counts[ext] += 1
            else:
                ext = file_.split('.')[-1]
                if ext not in extension_warnings:
                    print(f"warning: unknown extension '{ext}'", file=sys.stderr)
                    extension_warnings.add(ext)
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

    @staticmethod
    def get_empty_dirs(tree_dict, parent=""):
        empty_dirs = list()
        for dir_entry, children in tree_dict.items():
            # predicate
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
            # assertion function that returns, say, a boolean
            # assert_excessive_files(tree_dict, rule,
            if dir_entry == '_files':  # in tree_dict:
                if len(tree_dict['_files']) > bandbox.MAX_FILES:
                    dir_name = parent.ljust(LEFT_COL_WIDTH)
                    num_files = f"[{len(tree_dict['_files'])} files]"
                    excess.append(f"{dir_name}{num_files.rjust(RIGHT_COL_WIDTH - 3)}")
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

    @staticmethod
    def get_directories_with_mixed_files(tree_dict, parent=""):
        mixed_dirs = list()
        for dir_entry, children in tree_dict.items():
            if dir_entry == '_files':
                files = Tree.file_counts(tree_dict['_files'])
                if len(files) > 1:
                    mixed_dirs.append(f"{parent}")
            if isinstance(children, (dict, Tree)):
                mixed_dirs += Tree.get_directories_with_mixed_files(children, parent=f"{parent}{dir_entry}/")
        return mixed_dirs

    def find_directories_with_mixed_files(self) -> list:
        mixed_dirs = Tree.get_directories_with_mixed_files(self)
        return mixed_dirs

    @staticmethod
    def get_with_date_names(tree_dict, parent="") -> list:
        date_names = list()
        for dir_entry, children in tree_dict.items():
            if dir_entry == '_files':
                for file in tree_dict['_files']:
                    for date_cre in bandbox.DATE_CRE:
                        if date_cre.match(file):
                            date_names.append(f"{parent}{file}")
            if isinstance(children, (dict, Tree)):
                date_names += Tree.get_with_date_names(children, parent=f"{parent}{dir_entry}/")
        return list(set(date_names))

    def find_with_date_names(self) -> list:
        date_names = Tree.get_with_date_names(self)
        return date_names

    @staticmethod
    def get_accessions_in_names(tree_dict, parent=""):
        accession_names = list()
        for dir_entry, children in tree_dict.items():
            # start_eval
            if dir_entry == '_files':
                for file in tree_dict['_files']:
                    if bandbox.ACCESSION_NAMES_CRE.match(file):
                        accession_names.append(f"{parent}{file}")
            # end_eval
            if isinstance(children, (dict, Tree)):
                accession_names += Tree.get_accessions_in_names(children, parent=f"{parent}{dir_entry}/")
        return accession_names

    def find_accessions_in_names(self) -> list:
        accession_names = Tree.get_accessions_in_names(self)
        return accession_names

    @staticmethod
    def evaluate_predicate(tree_dict, assertion_callback, parent=""):
        """Generic rule to evaluate elements of the tree"""
        output = list()
        for dir_entry, children in tree_dict.items():
            # each method that finds something has to provide an assertion method which takes
            # - dir_entry: the current directory entry
            # - children: any children associated with the current directory
            # - tree_dict: the parent directory
            output += assertion_callback(dir_entry, children, tree_dict, parent)
            if isinstance(children, (dict, Tree)):
                output += Tree.evaluate_predicate(children, assertion_callback, parent=f"{parent}{dir_entry}/")
        return output

    def find_mixed_case(self) -> list:
        # todo: clarify the various arguments
        def mixed_case_predicate(dir_entry, children, parent_dir, parent):  # assertion callback for this 'find...' method
            output = list()
            if dir_entry == '_files':
                for file in parent_dir['_files']:
                    if re.match(r".*[A-Z].*", file) and re.match(r".*[a-z].*", file):
                        output.append(f"{parent}{file}")
            if re.match(r".*[A-Z].*", dir_entry) and re.match(r".*[a-z].*", dir_entry):
                output.append(f"{parent}{dir_entry}/")
            return output

        mixed_case = Tree.evaluate_predicate(self, mixed_case_predicate)
        return mixed_case
