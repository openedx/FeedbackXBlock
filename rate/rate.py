"""TO-DO: Write a description of what this XBlock is."""

import pkg_resources

from xblock.core import XBlock
from xblock.fields import Scope, Integer, String, List
from xblock.fragment import Fragment


class RateXBlock(XBlock):
    """
    TO-DO: document what your XBlock does.
    """

    # Fields are defined on the class.  You can access them in your code as
    # self.<fieldname>.

    levels = List(
        default=0, scope=Scope.settings,
        help="Names of ratings",
    )

    prompt = String(
        default=0, scope=Scope.settings,
        help="User prompt",
    )

    vote = Integer(
        default=-1, scope=Scope.user_state,
        help="How user voted. -1 if didn't vote",
    )

    vote_aggregate = List(
        default=0, scope=Scope.user_state_summary,
        help="A simple counter, to show something happening",
    )

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    # TO-DO: change this view to display your data your own way.
    def student_view(self, context=None):
        """
        The primary view of the RateXBlock, shown to students
        when viewing courses.
        """
        html = self.resource_string("static/html/rate.html")
        frag = Fragment(html.format(self=self))
        frag.add_css(self.resource_string("static/css/rate.css"))
        frag.add_javascript(self.resource_string("static/js/src/rate.js"))
        frag.initialize_js('RateXBlock')
        return frag

    # TO-DO: change this handler to perform your own actions.  You may need more
    # than one handler, or you may not need any handlers at all.
    @XBlock.json_handler
    def increment_count(self, data, suffix=''):
        """
        An example handler, which increments the data.
        """
        # Just to show data coming in...
        assert data['hello'] == 'world'

        self.count += 1
        return {"count": self.count}

    # TO-DO: change this to create the scenarios you'd like to see in the
    # workbench while developing your XBlock.
    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("RateXBlock",
             """<vertical_demo>
                <rate/>
                <rate/>
                <rate/>
                </vertical_demo>
             """),
        ]
