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

from bandbox import cli, core, utils

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
        self.assertFalse(args.display_paths)
        self.assertTrue(args.hide_file_counts)
        self.assertIsNone(args.input_file)

    def test_analyse(self):
        """Analyse the given path"""
        args = cli.cli(f"bandbox analyse")
        self.assertEqual('analyse', args.command)
        self.assertEqual(pathlib.Path('.'), args.path)


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
            tree = core.Tree()
            dir_entries = utils.scandir_recursive(TEST_DATA / data_name)
            [tree.insert(dir_entry, prefix=str(TEST_DATA)) for dir_entry in dir_entries]
            self.assertCountEqual(data, tree.data)

    def test_tree_insert_folder_with_one_file(self):
        tree = core.Tree()
        paths = ['folder', 'folder/file.txt']
        [tree.insert(path) for path in paths]
        self.assertEqual(
            {
                'folder': {
                    'files': ['file.txt']
                }
            },
            tree.data
        )

    def test_tree_insert_folder_with_one_folder(self):
        tree = core.Tree()
        paths = ['folder', 'folder/inner_folder']
        [tree.insert(path) for path in paths]
        print(tree.data)
        self.assertEqual(
            {
                'folder': {
                    'inner_folder': {}
                }
            },
            tree.data
        )

    def test_paths_must_be_folder(self):
        """Fail on file"""
        tree = core.Tree()
        paths = ['file.txt']


class TestAnalyse(Tests):
    def test_analyse_all_engines(self):
        """Run all engines"""


class TestUtils(Tests):
    def test_scandir_recursive(self):
        """Test that we can recursively scan a directory"""
        base_dir = TEST_DATA / "folder_with_single_file"
        path_generator = utils.scandir_recursive(base_dir)
        self.assertIsInstance(path_generator, types.GeneratorType)
        for dir_entry in path_generator:
            print(dir_entry, dir_entry.path)

    def test_scandir_recursive_filtering(self):
        """Test that we can exclude certain files"""
        test_dir = TEST_DATA / "folder_with_multiple_file_types"
        exclusion_list = ['*.txt']
        dir_entries = list(utils.scandir_recursive(test_dir, exclude=exclusion_list))
        print(dir_entries)
        self.assertTrue(False)
