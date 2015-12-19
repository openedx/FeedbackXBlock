# -*- coding: utf-8 -*-
"""
This file is just the bok_choy pages file for our icons. bok_choy
is a test framework, so we follow this split into pages/icon, although
it is a little artifical in this case.
"""
from bok_choy.page_object import PageObject


class IconsPage(PageObject):
    """
    We render our icons from HTML using bok_choy. bok_choy prefers
    working from a real web URL, and this is a page for the URL of the
    HTML file on github at the time of development
    (`pmitros/ux-revamp` branch). If we continue developing, this URL
    may need to change to `master` or otherwise. This should move from
    pmitros/ux-revamp branch to master at some point
    """

    url = '''
       https://rawgit.com/pmitros/RateXBlock/pmitros/ux-revamp/makeicons/raw_icons.html
    '''.strip()

    def is_browser_on_page(self):
        '''
        Check whether we have the fifth selected numeric icon. This is
        towards the bottom of the page.
        '''
        return self.q(css='#snum5').is_present()
