'''
This is a simple program which will capture icons from an HTML
Unicode font which can be used as happy/sad faces in the XBlock. We'd
rather use real fonts, but they render very poorly under some OSes
(Hello, Apple!), and may be missing on others (Hello,
Microsoft!). This script generally does not need to be rerun, but if
you would like to, we'd recommend running this under Ubuntu.
'''

import unittest
from bok_choy.web_app_test import WebAppTest
from pages import IconsPage


class TestIcons(WebAppTest):
    """
    Tests for the GitHub site.
    """

    def test_page_existence(self):
        """
        Make sure that the page is accessible.
        """
        page = IconsPage(self.browser)
        page.visit()
        self.assertScreenshot("#face1", "face1")
        self.assertScreenshot("#face2", "face2")
        self.assertScreenshot("#face3", "face3")
        self.assertScreenshot("#face4", "face4")
        self.assertScreenshot("#face5", "face5")

if __name__ == '__main__':
    unittest.main()
    
