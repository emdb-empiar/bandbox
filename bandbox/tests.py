"""
bandbox analyse # gives suggestions of possible violations
bandbox view    # render tree to show files and folders
"""
import unittest

import requests


class Tests(unittest.TestCase):
    """Base test class"""


class Test(Tests):
    def test_gist(self):
        """Get JSON data from Github gist"""
        response = requests.get(
            "https://gist.githubusercontent.com/paulkorir/5b71f57f7a29391f130e53c24a2db3fb/raw/da9142bb59479c278d1291165f1b416cf22030f8/bandbox.json")
        self.assertEqual(200, response.status_code)
        self.assertIsNotNone(response.text)
        self.assertIsInstance(response.json(), dict)
        self.assertTrue("file_formats" in response.json())


class TestAnalyse(Tests):
    def test_analyse_all_engines(self):
        """Run all engines"""
