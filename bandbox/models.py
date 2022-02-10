import os
import re
import sys
from collections import UserDict

import bandbox


class Tree(UserDict):
    def __new__(cls, sep='/', show_file_counts=True):
        cls.sep = sep
        cls.show_file_counts = show_file_counts
        return super().__new__(cls)

    @classmethod
    def from_data(cls, data, prefix="", show_file_counts=True, args=None):
        tree = cls()
        tree._args = args
        tree._configs = args._configs
        tree.show_file_counts = show_file_counts
        for t in data:
            tree.insert(t, prefix=prefix)
        return tree

    def insert(self, dir_entry: os.DirEntry, prefix: str = ''):
        """Insert the path into the tree creating nodes if necessary"""
        if prefix == '.':
            path_list = dir_entry.path.strip(self.sep).split(self.sep)
        else:
            path_list = dir_entry.path[len(prefix):].strip(self.sep).split(self.sep)
        # first, deal with directories
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

    # @staticmethod
    def file_counts(self, file_list):
        file_counts = dict()
        for file_ in file_list:
            file_match = self._configs.getcre('regex', 'file_re').match(file_)
            if file_match:
                ext = file_.split('.')[-1]
                if ext not in file_counts:
                    file_counts[ext] = 1
                else:
                    file_counts[ext] += 1
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
                        file_counts_str += f"{ext}={count}; "
                    string += f"{indent}└── [{len(value)} {item}: {file_counts_str}]\n"
                else:
                    string += f"{indent}└── [{len(value)} {item}]\n"

        return string

    def __str__(self):
        """Print as tree"""
        string = self._recursive_string(self.data)
        return string

    @staticmethod
    def evaluate_predicate(tree_dict, predicate, parent=""):
        """Generic rule to evaluate elements of the tree"""
        output = list()
        for dir_entry, children_dict in tree_dict.items():
            # each method that finds something has to provide an assertion method which takes
            # - dir_entry: the current directory entry
            # - children_dict: any children dictionary associated with the current directory
            # - tree_dict: the parent directory dictionary
            # - parent_path: string with the path to the dir_entry:
            output += predicate(dir_entry, children_dict, tree_dict, parent)
            if isinstance(children_dict, (dict, Tree)):
                output += Tree.evaluate_predicate(children_dict, predicate, parent=f"{parent}{dir_entry}/")
        return output

    def find_empty_directories(self, include_root=True) -> list:
        """Identify directories with no files"""

        def empty_directories_predicate(dir_entry, children_dict, parent_dict, parent_path):
            output = list()
            if len(children_dict) == 0:  # terminal empty folder
                output.append(f"{parent_path}{dir_entry}/")
            if len(children_dict) == 1:  # non-terminal folder with files only
                if "_files" not in children_dict and not isinstance(children_dict, list):
                    output.append(f"{parent_path}{dir_entry}/")
            return output

        empty_dirs = Tree.evaluate_predicate(self, empty_directories_predicate)
        if include_root:
            return empty_dirs
        return empty_dirs[1:]

    def find_obvious_directories(self, include_root=True) -> list:
        """Identify directories with obvious names"""

        def obvious_directories_predicate(dir_entry, children_dict, parent_dict, parent_path):
            output = list()
            if self._configs.getcre('regex', 'obvious_files_re').match(dir_entry):
                output.append(f"{parent_path}{dir_entry}/")
            return output

        obvious_directories = Tree.evaluate_predicate(self, obvious_directories_predicate)
        return obvious_directories

    def find_excessive_files_per_directory(self) -> list:
        """Identify directories with excessive files"""

        def excessive_files_per_directory_predicate(dir_entry, children_dict, parent_dict, parent_path):
            output = list()
            if dir_entry == '_files':  # in parent_dict:
                if len(parent_dict['_files']) > self._configs.getint('bandbox', 'max_files'):
                    # fixme: presentation logic bled in ---> remove
                    # dir_name = parent_path.ljust(LEFT_COL_WIDTH)
                    # num_files = f"[{len(parent_dict['_files'])} files]"
                    # output.append(f"{dir_name}{num_files.rjust(RIGHT_COL_WIDTH - 3)}")
                    output.append(f"{parent_path}")
            return output

        excess = Tree.evaluate_predicate(self, excessive_files_per_directory_predicate)
        return excess

    def find_long_names(self) -> list:
        """Identify path elements with long names"""

        def long_names_predicate(dir_entry, children_dict, parent_dict, parent_path):
            output = list()
            if len(dir_entry) > self._configs.getint('bandbox', 'max_name_length'):
                output.append(f"{parent_path}{dir_entry}/")
            return output

        long_names = Tree.evaluate_predicate(self, long_names_predicate)
        return long_names

    def find_directories_with_mixed_files(self) -> list:
        def directories_with_mixed_files_predicate(dir_entry, children_dict, parent_dict, parent_path):
            output = list()
            if dir_entry == '_files':
                files = self.file_counts(parent_dict['_files'])
                if len(files) > 1:
                    output.append(f"{parent_path}")
            return output

        mixed_dirs = Tree.evaluate_predicate(self, directories_with_mixed_files_predicate)
        return mixed_dirs

    def find_with_date_names(self) -> list:

        def date_names_predicate(dir_entry, children_dict, parent_dict, parent_path):
            output = list()
            if dir_entry == '_files':
                for file in parent_dict['_files']:
                    for date_re in map(lambda r: re.compile(r), self._configs.getlist('regex', 'date_re')):
                        if date_re.match(file):
                            output.append(f"{parent_path}{file}")
            return output

        date_names = list(set(Tree.evaluate_predicate(self, date_names_predicate)))
        return date_names

    def find_accessions_in_names(self) -> list:
        def accessions_in_names_predicate(dir_entry, chidren_dict, parent_dict, parent_path):
            output = list()
            if dir_entry == '_files':
                for file in parent_dict['_files']:
                    if self._configs.getcre('regex', 'accession_names_re').match(file):
                        output.append(f"{parent_path}{file}")
            return output

        accession_names = Tree.evaluate_predicate(self, accessions_in_names_predicate)
        return accession_names

    def find_mixed_case(self) -> list:
        """Find elements of the tree with names having mixed case"""

        def mixed_case_predicate(dir_entry, children_dict, parent_dict,
                                 parent_path):  # assertion callback for this 'find...' method
            output = list()
            if dir_entry == '_files':  # file contents
                for file in parent_dict['_files']:
                    if re.match(r".*[A-Z].*", file) and re.match(r".*[a-z].*", file):  # mixed case
                        output.append(f"{parent_path}{file}")
            if re.match(r".*[A-Z].*", dir_entry) and re.match(r".*[a-z].*", dir_entry):  # if the dirname has mixed case
                output.append(f"{parent_path}{dir_entry}/")
            return output

        mixed_case = Tree.evaluate_predicate(self, mixed_case_predicate)
        return mixed_case

    def find_odd_characters_in_names(self):
        """Find odd characters in path components"""

        def odd_characters_in_names_predicate(dir_entry, children_dict, parent_dict, parent_path):
            output = list()
            if dir_entry == '_files':
                for file in parent_dict['_files']:
                    if self._configs.getcre('regex', 'odd_chars_re').match(file):
                        output.append(f"{parent_path}{file}")
            if self._configs.getcre('regex', 'odd_chars_re').match(dir_entry):
                output.append(f"{parent_path}{dir_entry}/")
            return output

        odd_characters = Tree.evaluate_predicate(self, odd_characters_in_names_predicate)
        return odd_characters

    def find_excessive_periods_in_names(self):
        """Find odd characters in path components"""

        def excessive_periods_in_names_predicate(dir_entry, children_dict, parent_dict, parent_path):
            output = list()
            if dir_entry == '_files':
                for file in parent_dict['_files']:
                    if self._configs.getcre('regex', 'periods_in_name_fewer_than_re').match(file):
                        output.append(f"{parent_path}{file}")
            if self._configs.getcre('regex', 'periods_in_name_fewer_than_re').match(dir_entry):
                output.append(f"{parent_path}{dir_entry}/")
            return output

        odd_characters = Tree.evaluate_predicate(self, excessive_periods_in_names_predicate)
        return odd_characters

    def find_external_references_in_names(self):
        """Find external references in names"""

        def external_references_in_names_predicate(dir_entry, children_dict, parent_dict, parent_path):
            output = list()
            if dir_entry == '_files':
                for file in parent_dict['_files']:
                    if self._configs.getcre('regex', 'external_refs_re').match(file):
                        output.append(f"{parent_path}{file}")
            if self._configs.getcre('regex', 'external_refs_re').match(dir_entry):
                output.append(f"{parent_path}{dir_entry}/")
            return output

        external_refs = Tree.evaluate_predicate(self, external_references_in_names_predicate)
        return external_refs

    def find_unknown_file_extensions(self):
        """Find unknown file extensions"""
        def unknown_file_extensions_predicate(dir_entry, children_dict, parent_dict, parent_path):
            output = list()
            if dir_entry == '_files':
                for file in parent_dict['_files']:
                    if not self._configs.getcre('regex', 'file_extension_re').match(file):
                        output.append(f"{parent_path}{file}")
            return output

        unknown_exts = Tree.evaluate_predicate(self, unknown_file_extensions_predicate)
        return unknown_exts
