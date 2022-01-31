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
import os
import pathlib
import unittest

import requests

from bandbox import cli, core


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

    def test_get_path(self):
        tree = core.Tree()
        tree.data = {'a': {'b': {'c': 'd'}}}
        self.assertEqual('d', tree.get_path('a/b/c'))
        print(tree)

    def test_set_path(self):
        tree = core.Tree()
        tree.set_path('a/b/c/d')
        print(tree.data)
        self.assertEqual({'a': {'b': {'c': 'd'}}}, tree.data)
        self.assertEqual('d', tree.get_path('a/b/c'))

    def test_tree_insert_empty_dir(self):
        """Inserting paths into the tree"""
        tree = core.Tree()
        # path is single folder only
        dir_entries = os.scandir('/Users/pkorir/PycharmProjects/bandbox/test_data/empty_folder')
        [tree.insert(dir_entry) for dir_entry in dir_entries]
        # paths = [
        #     'folder',
        #     'folder/inner_folder1',
        #     'folder/inner_folder2',
        #     'folder/inner_folder1/file1.txt',
        #     'folder/inner_folder1/file2.txt',
        #     'folder/inner_folder1/file3.jpeg',
        #     'folder/inner_folder2/file1.txt',
        #     'folder/inner_folder2/file2.txt',
        #     'folder/inner_folder2/file3.jpeg',
        #     'folder/inner_folder2/inner_inner_folder',
        # ]
        # [tree.insert(path) for path in paths]
        # print(tree)
        print(tree.data)
        self.assertEqual({'root': {'type': 'directory', 'name': 'folder', 'contents': []}}, tree.data)

    def test_tree_insert_folder_with_one_file(self):
        tree = core.Tree()
        paths = ['folder', 'folder/file.txt']
        [tree.insert(path) for path in paths]
        print(tree.data)
        self.assertEqual(
            {
                'root': {
                    'type': 'directory',
                    'name': 'folder',
                    'contents': [
                        {
                            'type': 'file',
                            'name': 'file.txt'
                        }
                    ]
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
                'root': {
                    'type': 'directory',
                    'name': 'folder',
                    'contents': [
                        {
                            'type': 'directory',
                            'name': 'inner_folder',
                            'contents': []
                        }
                    ]
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
