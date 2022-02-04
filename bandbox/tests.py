"""
bandbox analyse # gives suggestions of possible violations
bandbox view    # render tree to show files and folders


inputs:
- file with tree
- path
- filtered path
output:
- display tree
- analyses
- save tree
"""
import pathlib
import types
import unittest

import requests

from bandbox import cli, core, utils, managers

BASE_DIR = pathlib.Path("/Users/pkorir/PycharmProjects/bandbox")
TEST_DATA = BASE_DIR / "test_data"


class Tests(unittest.TestCase):
    """Base test class"""


class Test(Tests):
    def test_gist(self):
        """Get JSON data from Github gist"""
        response = requests.get(
            "https://gist.githubusercontent.com/paulkorir/5b71f57f7a29391f130e53c24a2db3fb/raw/bandbox.json")
        self.assertEqual(200, response.status_code)
        self.assertIsNotNone(response.text)
        self.assertIsInstance(response.json(), dict)
        self.assertTrue("file_formats" in response.json())


class TestCLI(Tests):
    """BDD for the CLI"""

    def test_view(self):
        """View the tree"""
        args = cli.cli(f"bandbox view")
        self.assertEqual('view', args.command)
        self.assertEqual(pathlib.Path('.'), args.path)
        self.assertEqual('', args.prefix)
        self.assertFalse(args.verbose)
        self.assertTrue(args.hide_file_counts)
        self.assertIsNone(args.input_file)

    def test_analyse(self):
        """Analyse the given path"""
        args = cli.cli(f"bandbox analyse")
        self.assertEqual('analyse', args.command)
        self.assertEqual(pathlib.Path('.'), args.path)
        self.assertFalse(args.include_root)
        self.assertFalse(args.summarise)
        self.assertEqual(5, args.summarise_size)


class TestCore(Tests):
    """Test core entities"""

    def test_tree_init(self):
        """Initialise a tree"""
        tree = core.Tree()
        self.assertIsInstance(tree, core.Tree)
        self.assertTrue(hasattr(tree, 'data'))  # as a UserDict subclass this is where the data sits
        self.assertTrue(hasattr(tree, 'sep'))
        self.assertTrue(hasattr(tree, 'show_file_counts'))

    def test_tree_insert(self):
        """Test inserting paths into the tree"""
        expected_output = dict(
            empty_folder={'empty_folder': {'folder': {}}},
            folder_with_multiple_file_types={
                'folder_with_multiple_file_types': {
                    'folder': {
                        'files': [f"file{i}.tif" for i in range(1, 11)] + [f"file{j}.txt" for j in range(1, 11)]}}
            },
            folder_with_multiple_files={
                'folder_with_multiple_files': {'folder': {'files': [f"file{j}.txt" for j in range(1, 11)]}}
            },
            folder_with_multiple_folders={
                'folder_with_multiple_folders': {
                    f"folder{i}": [f"file{j}.tif" for j in range(1, 11)] for i in range(1, 6)
                }
            },
            folder_with_single_file={'folder_with_single_file': {'folder': {'files': ['file.txt']}}},
            single_empty_folder={'single_empty_folder': {'folder': {}}},
        )
        for data_name, data in expected_output.items():
            dir_entries = utils.scandir_recursive(TEST_DATA / data_name)
            tree = core.Tree.from_data(dir_entries, prefix=str(TEST_DATA))
            # the best we can do is compare keys
            self.assertListEqual(list(data.keys()), list(tree.data.keys()))

    def test_all_find_methods(self):
        """Test all find methods

        There is no need to write a method for each when the only thing that changes is the data. Rather, we compile
        all the data into a dictionary and only update the dictionary as we add new find methods.

        Each find method on the tree will need:
        - the method name
        - the name of the source folder
        - the expected output
        - a tree instance (created on the fly)
        """
        data = [
            # {
            #     "tree_method": "find_mixed_case",
            #     "source_folder": "folder_with_multiple_files",
            #     "expected_value": ['folder_with_multiple_files/folder/file-EMPIAR-someting.tif']
            # },
            # {
            #     "tree_method": "find_accessions_in_names",
            #     "source_folder": "folder_with_multiple_files",
            #     "expected_value": ['folder_with_multiple_files/folder/file-EMPIAR-someting.tif']
            # },
            # {
            #     "tree_method": "find_with_date_names",
            #     "source_folder": "folder_with_date_name_files",
            #     "expected_value": [
            #         'folder_with_date_name_files/prefix-12312000-suffix.txt',
            #         'folder_with_date_name_files/prefix-2000:12:31-suffix.txt',
            #         'folder_with_date_name_files/prefix-31:December:2000-suffix.txt',
            #         'folder_with_date_name_files/prefix-31122000-suffix.txt',
            #         'folder_with_date_name_files/prefix-31-Dec-2000-suffix.txt',
            #         'folder_with_date_name_files/prefix-Dec-31-2000-suffix.txt',
            #         'folder_with_date_name_files/prefix-2000-12-31-suffix.txt',
            #         'folder_with_date_name_files/prefix-20001231-suffix.txt',
            #         'folder_with_date_name_files/prefix-001231-suffix.txt',
            #         'folder_with_date_name_files/prefix-31-December-2000-suffix.txt'
            #     ]
            # },
            # {
            #     "tree_method": "find_directories_with_mixed_files",
            #     "source_folder": "folder_with_multiple_file_types",
            #     "expected_value": ['folder_with_multiple_file_types/folder/']
            # },
            # {
            #     "tree_method": "find_long_names",
            #     "source_folder": "folder_with_long_name_folders",
            #     "expected_value": [
            #         'folder_with_long_name_folders',
            #         'folder_with_long_name_folders/a folder with & funny symbols in the ?? name',
            #         'folder_with_long_name_folders/a folder with spaces in the name',
            #         'folder_with_long_name_folders/a_folder_with_a_very_long_name_that_we_cannot_even_begin_to_comprehend',
            #         'folder_with_long_name_folders/folder/inner_folder/another_very_long_name_that_we_are_still_wondering_'
            #         'ever_found_the_light_of_day'
            #     ]
            # },
            # {
            #     "tree_method": "find_excessive_files_per_directory",
            #     "source_folder": "folder_with_multiple_folders",
            #     "expected_value": [f'folder_with_multiple_folders/folder{i}/' for i in range(1, 6)]
            # },
            # {
            #     "tree_method": "find_obvious_directories",
            #     "source_folder": "single_empty_folder",
            #     "expected_value": ['single_empty_folder/folder', 'single_empty_folder/folder/inner_folder']
            # },
            # {
            #     "tree_method": "find_obvious_directories",
            #     "source_folder": "folder_with_multiple_file_types",
            #     "expected_value": [
            #         'folder_with_multiple_file_types/folder',
            #         'folder_with_multiple_file_types/folder/files',
            #         'folder_with_multiple_file_types/folder/inner_folder'
            #     ]
            # },
            # {
            #     "tree_method": "find_empty_directories",
            #     "source_folder": "single_empty_folder",
            #     "expected_value": [
            #         'single_empty_folder',
            #         'single_empty_folder/folder',
            #         'single_empty_folder/folder/inner_folder'
            #     ]
            # },
            # {
            #     "tree_method": "find_empty_directories",
            #     "source_folder": "single_empty_folder",
            #     "expected_value": [
            #         'single_empty_folder/folder',
            #         'single_empty_folder/folder/inner_folder'
            #     ],
            #     "kwargs": {"include_root": False}
            # },
            # {
            #     "tree_method": "find_empty_directories",
            #     "source_folder": "empty_folder",
            #     "expected_value": ['empty_folder', 'empty_folder/folder'],
            # },
            # {
            #     "tree_method": "find_empty_directories",
            #     "source_folder": "folder_with_multiple_folders",
            #     "expected_value": [],
            # },
            # {
            #     "tree_method": "find_empty_directories",
            #     "source_folder": "folder_with_multiple_folders",
            #     "expected_value": [],
            #     "kwargs": {"include_root": False}
            # },
            # {
            #     "tree_method": "find_empty_directories",
            #     "source_folder": "folder_with_multiple_file_types",
            #     "expected_value": [
            #         'folder_with_multiple_file_types',
            #         'folder_with_multiple_file_types/folder/files',
            #         'folder_with_multiple_file_types/folder/inner_folder'
            #     ],
            # },
            # {
            #     "tree_method": "find_empty_directories",
            #     "source_folder": "folder_with_multiple_file_types",
            #     "expected_value": [
            #         'folder_with_multiple_file_types/folder/files',
            #         'folder_with_multiple_file_types/folder/inner_folder'
            #     ],
            #     "kwargs": {"include_root": False}
            # },
            # {
            #     "tree_method": "find_odd_characters_in_names",
            #     "source_folder": "folder_with_long_name_folders",
            #     "expected_value": [
            #         'folder_with_long_name_folders/a folder with & funny symbols in the ?? name',
            #         'folder_with_long_name_folders/a folder with spaces in the name'
            #     ],
            # },
            # {
            #     "tree_method": "find_excessive_periods_in_names",
            #     "source_folder": "folder_with_long_name_folders",
            #     "expected_value": [
            #         'folder_with_long_name_folders/a.folder.with.periods.in.the.name',
            #         'folder_with_long_name_folders/folder/a.file.with.many.periods.txt'
            #     ],
            # },
            # {
            #     "tree_method": "find_external_references_in_names",
            #     "source_folder": "folder_with_long_name_folders",
            #     "expected_value": [
            #         'folder_with_long_name_folders/folder/figure5.jpg',
            #         'folder_with_long_name_folders/folder/supplementary-figure3a.jpg',
            #     ],
            # },
            {
                "tree_method": "find_unknown_file_extensions",
                "source_folder": "folder_with_long_name_folders",
                "expected_value": [
                    'folder_with_long_name_folders/folder/file.wrx',
                    'folder_with_long_name_folders/folder/file.onx',
                    'folder_with_long_name_folders/folder/file.dog',

                ],
            },
        ]
        for data_dict in data:
            dir_entries = utils.scandir_recursive(TEST_DATA / data_dict["source_folder"])
            tree = core.Tree.from_data(dir_entries, prefix=str(TEST_DATA))
            if "kwargs" in data_dict:
                result = sorted(
                    getattr(
                        tree,
                        data_dict["tree_method"]
                    )(**data_dict["kwargs"])
                )
            else:
                result = sorted(getattr(tree, data_dict["tree_method"])())
            self.assertEqual(sorted(data_dict["expected_value"]), result)


class TestAnalyse(Tests):
    def test_analyse_all_engines(self):
        """Run all engines"""
        args = cli.cli(f"bandbox analyse {TEST_DATA / 'empty_folder'}")
        managers.analyse(args)


class TestUtils(Tests):
    def test_scandir_recursive(self):
        """Test that we can recursively scan a directory"""
        base_dir = TEST_DATA / "folder_with_single_file"
        path_generator = utils.scandir_recursive(base_dir)
        self.assertIsInstance(path_generator, types.GeneratorType)
        for dir_entry in path_generator:
            print(dir_entry, dir_entry.path)

    # def test_scandir_recursive_filtering(self):
    #     """Test that we can exclude certain files"""
    #     test_dir = TEST_DATA / "folder_with_multiple_file_types"
    #     exclusion_list = ['*.txt']
    #     dir_entries = list(utils.scandir_recursive(test_dir, exclude=exclusion_list))
    #     print(dir_entries)
    #     self.assertTrue(False)
