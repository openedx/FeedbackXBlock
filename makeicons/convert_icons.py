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
from .pages import IconsPage


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
        for i in range(5):
            for icon in ["face", "num"]:
                for style in "ais":
                    self.assertScreenshot("#"+style+icon+str(i+1),
                                          style+icon+str(i+1))


if __name__ == '__main__':
    unittest.main()
