# coding: utf-8
"""
This is an XBlock designed to allow people to provide feedback on our
course resources.
"""

import random

import pkg_resources

from xblock.core import XBlock
from xblock.fields import Scope, Integer, String, List, Float
from xblock.fragment import Fragment

try:
    from eventtracking import tracker
except ImportError:
    class tracker(object):  # pylint: disable=invalid-name
        """
        Define tracker if eventtracking cannot be imported. This is a workaround
        so that the code works in both edx-platform and XBlock workbench (the latter
        of which does not support event emission). This should be replaced with XBlock's
        emit(), but at present, emit() is broken.
        """
        def __init__(self):
            """ Do nothing """
            pass

        @staticmethod
        def emit(param1, param2):
            """ In workbench, do nothing for event emission """
            pass

class RateXBlock(XBlock):
    """
    This is an XBlock -- eventually, hopefully an aside -- which
    allows you to rate content in the course. We've wanted this for a
    long time, but Dartmouth finally encourage me to start to build
    this.
    """

    default_prompt = {'freeform':"Please provide us feedback on this section.",
                      'likert':"Please rate your overall experience with this section.",
                      'mouseovers':["Excellent", "Good", "Average", "Fair", "Poor"],
                      'icons':[u"😁",u"😊",u"😐",u"☹",u"😟"]}
    
    # This is a list of prompts. If we have multiple elements in the
    # list, one will be chosen at random. This is currently not
    # exposed in the UX. If the prompt is missing any portions, we
    # will default to the ones in default_prompt.
    prompts = List(
        default=[{'freeform':"What could be improved to make this section more clear?",
                  'likert':"Was this section clear or confusing?"}], 
        scope=Scope.settings,
        help="Freeform user prompt",
        xml_node = True
    )

    prompt_choice = Integer(
        default=-1, scope=Scope.user_state,
        help="Random number generated for p. -1 if uninitialized"
    )

    user_vote = Integer(
        default=-1, scope=Scope.user_state,
        help="How user voted. -1 if didn't vote"
    )

    p = Float(
        default=100, scope=Scope.settings,
        help="What percent of the time should this show?"
    )

    p_r = Float(
        default=-1, scope=Scope.user_state,
        help="Random number generated for p. -1 if uninitialized"
    )

    
    vote_aggregate = List(
        default=None, scope=Scope.user_state_summary,
        help="A list of user votes"
    )

    user_freeform = String(default = "", scope=Scope.user_state,
                        help = "Feedback")

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def get_prompt(self, index):
        """
        Return the current prompt dictionary, doing appropriate
        randomization if necessary, and falling back to defaults when
        necessary.
        """
        prompt = dict(self.default_prompt)
        prompt.update(self.prompts[index])
        return prompt

    def student_view(self, context=None):
        """
        The primary view of the RateXBlock, shown to students
        when viewing courses.
        """
        if self.prompt_choice < 0 or self.prompt_choice >= len(self.prompts):
            self.prompt_choice = random.randint(0, len(self.prompts)-1)        
        prompt = self.get_prompt(self.prompt_choice)

        # Figure out which prompt we show. We set self.prompt_choice to
        # the index of the prompt. We set it if it is out of range (either
        # uninitiailized, or incorrect due to changing list length). Then,
        # we grab the prompt, prepopulated with defaults.

        # Now, we render the RateXBlock. This may be redundant, since we
        # don't always show it.
        html = self.resource_string("static/html/rate.html")
        # The replace allows us to format the HTML nicely without getting
        # extra whitespace
        scale_item = self.resource_string("static/html/scale_item.html").replace('\n','')
        indexes = range(len(prompt['icons']))
        active_vote = ["checked" if i == self.user_vote else "" for i in indexes]
        scale = u"".join(scale_item.format(level=level, icon=icon, i=i, active=active) for (level,icon,i,active) in zip(prompt['mouseovers'], prompt['icons'], indexes, active_vote))
        rendered = html.format(self=self, scale=scale, freeform_prompt = prompt['freeform'], likert_prompt = prompt['likert'])

        # We initialize self.p_r if not initialized -- this sets whether
        # or not we show it. From there, if it is less than odds of showing,
        # we set the fragment to the rendered XBlock. Otherwise, we return
        # empty HTML. There ought to be a way to return None, but XBlocks
        # doesn't support that. 
        if self.p_r == -1:
            self.p_r = random.uniform(0, 100)
        if self.p_r < self.p:
            frag = Fragment(rendered)
        else:
            frag = Fragment(u"")

        # Finally, we do the standard JS+CSS boilerplate. Honestly, XBlocks
        # ought to have a sane default here.
        frag.add_css(self.resource_string("static/css/rate.css"))
        frag.add_javascript(self.resource_string("static/js/src/rate.js"))
        frag.initialize_js('RateXBlock')
        return frag

    def studio_view(self, context):
        """
        Create a fragment used to display the edit view in the Studio.
        """
        html_str = pkg_resources.resource_string(__name__, "static/html/studio_view.html")
        prompt = self.get_prompt(0)
        frag = Fragment(unicode(html_str).format(**prompt))
        js_str = pkg_resources.resource_string(__name__, "static/js/src/studio.js")
        frag.add_javascript(unicode(js_str))
        frag.initialize_js('RateBlock')
        return frag

    @XBlock.json_handler
    def studio_submit(self, data, suffix=''):
        """
        Called when submitting the form in Studio.
        """
        print data
        self.prompts[0]['freeform'] = data.get('freeform')
        self.prompts[0]['likert'] = data.get('likert')
        return {'result': 'success'}

    def vote(self, data):
        """
        Handle voting
        """
        # prompt_choice is initialized by student view.
        # Ideally, we'd break this out into a function.
        prompt = self.get_prompt(self.prompt_choice)

        # Make sure we're initialized
        if not self.vote_aggregate:
            self.vote_aggregate = [0]*len(prompt['mouseovers'])

        # Remove old vote if we voted before
        if self.user_vote != -1:
            self.vote_aggregate[self.user_vote] -= 1


        self.user_vote = data['vote']
        self.vote_aggregate[self.user_vote] += 1

    @XBlock.json_handler
    def feedback(self, data, suffix=''):
        if 'freeform' in data:
            tracker.emit('edx.ratexblock.freeform_feedback', 
                         {'old_freeform' : self.user_freeform, 
                          'new_freeform' : data['freeform']})
            self.user_freeform = data['freeform']
        if 'vote' in data:
            tracker.emit('edx.ratexblock.likert_rate', 
                         {'old_vote' : self.user_vote,
                          'new_vote' : data['vote']})
            self.vote(data)
        return {"success": True}

    # TO-DO: change this to create the scenarios you'd like to see in the
    # workbench while developing your XBlock.
    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("RateXBlock",
             """<vertical_demo>
                <rate p="50"/>
                <rate p="50"/>
                <rate p="50"/>
                </vertical_demo>
             """),
        ]
