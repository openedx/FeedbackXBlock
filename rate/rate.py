# coding: utf-8
"""
This is an XBlock designed to allow people to provide feedback on our
course resources, and to think and synthesize about their experience
in the course.
"""

import random

import pkg_resources

from xblock.core import XBlock
from xblock.fields import Scope, Integer, String, List, Float
from xblock.fragment import Fragment

"""
We provide default text which is designed to elicit student thought. We'd
like instructors to customize this to something highly structured (not 
"What did you think?" and "How did you like it?".
"""
default_freeform = "What did you learn from this? What was missing?"
default_likert = "How would you rate this as a learning experience?"
default_default = "Think about the material, and try to synthesize key " \
                  "lessons learned, as well as key gaps in our presentation."
default_placeholder = "Take a little bit of time to reflect here. " \
                      "Research shows that a meaningful synthesis will help " \
                      "you better understand and remember material from this" \
                      "course."
default_icon = "face"

@XBlock.needs('i18n')
class RateXBlock(XBlock):
    """
    This is an XBlock -- eventually, hopefully an aside -- which
    allows you to rate content in the course. We've wanted this for a
    long time, but Dartmouth finally encourage me to start to build
    this.
    """
    # This is a list of prompts. If we have multiple elements in the
    # list, one will be chosen at random. This is currently not
    # exposed in the UX. If the prompt is missing any portions, we
    # will default to the ones in default_prompt.
    prompts = List(
        default=[
            {'freeform': default_freeform,
             'default_text': default_default,
             'likert': default_likert,
             'placeholder': default_placeholder}
        ],
        scope=Scope.settings,
        help="Freeform user prompt",
        xml_node=True
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

    p_user = Float(
        default=-1, scope=Scope.user_state,
        help="Random number generated for p. -1 if uninitialized"
    )

    vote_aggregate = List(
        default=None, scope=Scope.user_state_summary,
        help="A list of user votes"
    )

    user_freeform = String(default="", scope=Scope.user_state,
                           help="Feedback")

    display_name = String(
        display_name="Display Name",
        default="Provide Feedback",
        scopde=Scope.settings
    )

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def get_prompt(self, index=-1):
        """
        Return the current prompt dictionary, doing appropriate
        randomization if necessary, and falling back to defaults when
        necessary.
        """
        if index == -1:
            index = self.prompt_choice

        _ = self.runtime.service(self, 'i18n').ugettext
        prompt = {
            'freeform': _("Please reflect on this course material"),
            'default_text': _("Please take time to meaningfully reflect "
                              "on your experience with this course "
                              "material."),
            'likert': _("Please rate your overall experience"),
            'scale_text': [_("Excellent"),
                           _("Good"),
                           _("Average"),
                           _("Fair"),
                           _("Poor")],
            'icons': [u"😁", u"😊", u"😐", u"😞", u"😭"],
            'placeholder': ["Please take a moment to thoughtfully reflect."]
        }

        prompt.update(self.prompts[index])
        return prompt

    def student_view(self, context=None):
        """
        The primary view of the RateXBlock, shown to students
        when viewing courses.
        """
        # Figure out which prompt we show. We set self.prompt_choice to
        # the index of the prompt. We set it if it is out of range (either
        # uninitiailized, or incorrect due to changing list length). Then,
        # we grab the prompt, prepopulated with defaults.
        if self.prompt_choice < 0 or self.prompt_choice >= len(self.prompts):
            self.prompt_choice = random.randint(0, len(self.prompts) - 1)
        prompt = self.get_prompt()

        # Now, we render the RateXBlock.
        html = self.resource_string("static/html/rate.html")

        # Staff see vote totals, so we have slightly different HTML here.
        if self.vote_aggregate and self.is_staff():
            scale_item = self.resource_string("static/html/staff_item.html")
        else:
            scale_item = self.resource_string("static/html/scale_item.html")
        # The replace allows us to format the HTML nicely without getting
        # extra whitespace
        scale_item = scale_item.replace('\n', '')

        # We have five Likert fields right now, but we'd like this to
        # be dynamic
        indexes = range(len(prompt['icons']))

        # If the user voted before, we'd like to show that
        active_vote = ["checked" if i == self.user_vote else ""
                       for i in indexes]

        # Confirm that we do have vote totals (this may be uninitialized
        # otherwise). This should probably go into __init__ or similar.
        self.init_vote_aggregate()
        votes = self.vote_aggregate

        # We grab the icons. This should move to a Filesystem field so
        # instructors can upload new ones
        ina_templ = 'public/default_icons/iface{i}.png'
        act_templ = 'public/default_icons/aface{i}.png'
        sel_templ = 'public/default_icons/sface{i}.png'
        ina_urls = [self.runtime.local_resource_url(self, ina_templ.format(i=i))
                    for i in range(1,6)]
        act_urls = [self.runtime.local_resource_url(self, act_templ.format(i=i))
                    for i in range(1,6)]
        sel_urls = [self.runtime.local_resource_url(self, sel_templ.format(i=i))
                    for i in range(1,6)]
        img_urls = [i if active else a
                    for (i, active, a)
                    in zip(ina_urls, active_vote, act_urls)]

        # Render the 
        scale = u"".join(
            scale_item.format(scale_text=scale_text,
                              unicode_icon=unicode_icon,
                              idx=idx,
                              active=active,
                              vote_cnt=vote_cnt,
                              ina_icon=ina_icon,
                              act_icon=act_icon,
                              sel_icon=sel_icon) for
            (scale_text,
             unicode_icon,
             idx,
             active,
             vote_cnt,
             act_icon,
             ina_icon,
             sel_icon) in
            zip(prompt['scale_text'],
                prompt['icons'],
                indexes,
                active_vote,
                votes,
                act_urls,
                ina_urls,
                sel_urls
            )
        )
        if self.user_vote != -1:
            _ = self.runtime.service(self, 'i18n').ugettext
            response = _("Thank you for voting!")
        else:
            response = ""
        rendered = html.format(self=self,
                               scale=scale,
                               freeform_prompt=prompt['freeform'],
                               likert_prompt=prompt['likert'],
                               response=response)

        # We initialize self.p_user if not initialized -- this sets whether
        # or not we show it. From there, if it is less than odds of showing,
        # we set the fragment to the rendered XBlock. Otherwise, we return
        # empty HTML. There ought to be a way to return None, but XBlocks
        # doesn't support that.
        if self.p_user == -1:
            self.p_user = random.uniform(0, 100)
        if self.p_user < self.p:
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
        html_str = self.resource_string("static/html/studio_view.html")
        prompt = self.get_prompt(0)
        frag = Fragment(unicode(html_str).format(**prompt))
        js_str = self.resource_string("static/js/src/studio.js")
        frag.add_javascript(unicode(js_str))
        frag.initialize_js('RateBlock')
        return frag

    @XBlock.json_handler
    def studio_submit(self, data, suffix=''):
        """
        Called when submitting the form in Studio.
        """
        self.prompts[0]['freeform'] = data.get('freeform')
        self.prompts[0]['likert'] = data.get('likert')
        return {'result': 'success'}

    def init_vote_aggregate(self):
        # Make sure we're initialized
        if not self.vote_aggregate:
            self.vote_aggregate = [0] * (len(self.get_prompt()['scale_text']))

    def vote(self, data):
        """
        Handle voting
        """
        # prompt_choice is initialized by student view.
        # Ideally, we'd break this out into a function.
        prompt = self.get_prompt(self.prompt_choice)

        # Make sure we're initialized
        self.init_vote_aggregate()

        # Remove old vote if we voted before
        if self.user_vote != -1:
            self.vote_aggregate[self.user_vote] -= 1

        self.user_vote = data['vote']
        self.vote_aggregate[self.user_vote] += 1

    @XBlock.json_handler
    def feedback(self, data, suffix=''):
        '''
        Allow students to submit feedback, both numerical and
        qualitative. We only update the specific type of feedback
        submitted.

        We return the current state. While this is not used by the
        client code, it is helpful for testing. For staff users, we
        also return the aggregate results.
        '''
        _ = self.runtime.service(self, 'i18n').ugettext

        if 'freeform' not in data and 'vote' not in data:
            response = {"success": False,
                        "response": _("Please vote!")}
            self.runtime.publish(self,
                                 'edx.ratexblock.nothing_provided',
                                 {})
        if 'vote' in data:
            response = {"success": True,
                        "response": _("Thank you for voting!")}
            self.runtime.publish(self,
                         'edx.ratexblock.likert_provided',
                         {'old_vote': self.user_vote,
                          'new_vote': data['vote']})
            self.vote(data)
        if 'freeform' in data:
            response = {"success": True,
                        "response": _("Thank you for your feedback!")}
            self.runtime.publish(self,
                                 'edx.ratexblock.freeform_provided',
                                 {'old_freeform': self.user_freeform,
                                 'new_freeform': data['freeform']})
            self.user_freeform = data['freeform']

        response.update({
            "freeform": self.user_freeform,
            "vote": self.user_vote
        })

        if self.is_staff():
            response['aggregate'] = self.vote_aggregate

        return response

    # TO-DO: change this to create the scenarios you'd like to see in the
    # workbench while developing your XBlock.
    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("RateXBlock",
             """<vertical_demo>
                <rate p="100"/>
                <!--rate p="50"/>
                <rate p="50"/-->
                </vertical_demo>
             """),
        ]

    def is_staff(self):
        """
        Return self.xmodule_runtime.user_is_staff if available

        This is not a supported part of the XBlocks API in all
        runtimes, and this is a workaround so something reasonable
        happens in both workbench and edx-platform
        """
        if hasattr(self, "xmodule_runtime") and \
           hasattr(self.xmodule_runtime, "user_is_staff"):
            return self.xmodule_runtime.user_is_staff
        else:
            # In workbench and similar settings, always return true
            return True
