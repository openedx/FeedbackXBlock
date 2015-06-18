# coding: utf-8
"""
This is an XBlock designed to allow people to provide feedback on our
course resources.
"""


import pkg_resources

from xblock.core import XBlock
from xblock.fields import Scope, Integer, String, List
from xblock.fragment import Fragment


class RateXBlock(XBlock):
    """
    This is an XBlock -- eventually, hopefully an aside -- which
    allows you to rate content in the course. We've wanted this for a
    long time, but Dartmouth finally encourage me to start to build
    this.
    """

    mouseover_levels = List(
        default=["Excellent", "Good", "Average", "Fair", "Poor"],
        scope=Scope.settings,
        help="Names of ratings for Likert-like scale"
    )

    mouseover_icons = List(
        default=[u"😁",u"☺",u"😐",u"☹",u"😟"],
        scope=Scope.settings,
        help="Names of ratings for Likert-like scale"
    )

    string_prompt = String(
        default="Please provide us feedback on this section.", 
        scope=Scope.settings,
        help="Freeform user prompt"
    )

    likert_prompt = String(
        default="Please rate your overall experience with this section.", 
        scope=Scope.settings,
        help="Likert-like scale user prompt"
    )

    user_vote = Integer(
        default=-1, scope=Scope.user_state,
        help="How user voted. -1 if didn't vote"
    )

    vote_aggregate = List(
        default=None, scope=Scope.user_state_summary,
        help="A list of user votes"
    )

    user_feedback = String(default = "", scope=Scope.user_state,
                        help = "Feedback")

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def student_view(self, context=None):
        """
        The primary view of the RateXBlock, shown to students
        when viewing courses.
        """
        html = self.resource_string("static/html/rate.html")
        scale_item = u'<span class="rate_likert_rating rate_rating_{i} {active}" title="{level}">{icon}</span>'
        indexes = range(len(self.mouseover_icons))
        active_vote = [" rate_rating_active " if i == self.user_vote else "" for i in indexes]
        scale = u"".join(scale_item.format(level=level, icon=icon, i=i, active=active) for (level,icon,i,active) in zip(self.mouseover_levels, self.mouseover_icons, indexes, active_vote))
        frag = Fragment(html.format(self=self, scale=scale))
        frag.add_css(self.resource_string("static/css/rate.css"))
        frag.add_javascript(self.resource_string("static/js/src/rate.js"))
        frag.initialize_js('RateXBlock')
        return frag

    @XBlock.json_handler
    def vote(self, data, suffix=''):
        """
        Handle voting
        """
        # Make sure we're initialized
        if not self.vote_aggregate:
            self.vote_aggregate = [0]*len(self.mouseover_levels)

        # Remove old vote if we voted before
        if self.user_vote != -1:
            self.vote_aggregate[self.user_vote] -= 1

        self.user_vote = data['vote']
        self.vote_aggregate[self.user_vote] += 1
        return {"success": True}

    @XBlock.json_handler
    def feedback(self, data, suffix=''):
        self.user_feedback = data['feedback']

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
