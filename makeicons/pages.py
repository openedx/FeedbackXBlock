# -*- coding: utf-8 -*-
from bok_choy.page_object import PageObject

class IconsPage(PageObject):
    """
    GitHub's search page
    """

    url = 'https://rawgit.com/pmitros/RateXBlock/master/makeicons/raw_icons.html'

    def is_browser_on_page(self):
        return self.q(css='#face5').is_present()
