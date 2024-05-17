# pylint: disable=E1101
# coding: utf-8
"""
This is an XBlock designed to allow people to provide feedback on our
course resources, and to think and synthesize about their experience
in the course.
"""

import html
import random
import pkg_resources
import six

from xblock.core import XBlock
from xblock.fields import Scope, Integer, String, List, Float, Boolean
from web_fragments.fragment import Fragment
from feedback.utils import _
try:
    from xblock.utils.resources import ResourceLoader
except ModuleNotFoundError:  # For backward compatibility with releases older than Quince.
    from xblockutils.resources import ResourceLoader

resource_loader = ResourceLoader(__name__)

# We provide default text which is designed to elicit student thought. We'd
# like instructors to customize this to something highly structured (not
# "What did you think?" and "How did you like it?".
DEFAULT_FREEFORM = _("What did you learn from this? What was missing?")
DEFAULT_LIKERT = _("How would you rate this as a learning experience?")
DEFAULT_DEFAULT = _(
    "Think about the material, and try to synthesize key "
    "lessons learned, as well as key gaps in our presentation."
)
DEFAULT_PLACEHOLDER = _(
    "Take a little bit of time to reflect here. "
    "Research shows that a meaningful synthesis will help "
    "you better understand and remember material from "
    "this course."
)
DEFAULT_ICON = "face"
DEFAULT_SCALETEXT = [_("Excellent"), _("Good"), _("Average"), _("Fair"), _("Poor")]

# Unicode alt faces are cute, but we do nulls instead for a11y.
ICON_SETS = {
    "face": [""] * 5,  # u"😁😊😐😞😭",
    "num": "12345",
    "midface": [""] * 5,  # u"😞😐😊😐😞"
    "star": [""] * 5,  # u "☆☆☆☆☆"
}


@XBlock.needs('i18n')
class FeedbackXBlock(XBlock):
    """
    This is an XBlock -- eventually, hopefully an aside -- which
    allows you to feedback content in the course. We've wanted this for a
    long time, but Dartmouth finally encourage me to start to build
    this.
    """
    # This is a list of prompts. If we have multiple elements in the
    # list, one will be chosen at random. This is currently not
    # exposed in the UX. If the prompt is missing any portions, we
    # will default to the ones in default_prompt.
    prompts = List(
        default=[
            {
                "freeform": DEFAULT_FREEFORM,
                "default_text": DEFAULT_DEFAULT,
                "likert": DEFAULT_LIKERT,
                "placeholder": DEFAULT_PLACEHOLDER,
                "scale_text": DEFAULT_SCALETEXT,
                "icon_set": DEFAULT_ICON,
            }
        ],
        scope=Scope.settings,
        help=_("Freeform user prompt"),
        xml_node=True
    )

    prompt_choice = Integer(
        default=-1, scope=Scope.user_state,
        help=_("Random number generated for p. -1 if uninitialized")
    )

    user_vote = Integer(
        default=-1, scope=Scope.user_state,
        help=_("How user voted. -1 if didn't vote")
    )

    # pylint: disable=invalid-name
    p = Float(
        default=100, scope=Scope.settings,
        help=_("What percent of the time should this show?")
    )

    p_user = Float(
        default=-1, scope=Scope.user_state,
        help=_("Random number generated for p. -1 if uninitialized")
    )

    vote_aggregate = List(
        default=None, scope=Scope.user_state_summary,
        help=_("A list of user votes")
    )

    user_freeform = String(default="", scope=Scope.user_state,
                           help=_("Feedback"))

    display_name = String(
        display_name=_("Display Name"),
        default=_("Provide Feedback"),
        scopde=Scope.settings
    )

    voting_message = String(
        display_name=_("Voting message"),
        default=_("Thank you for voting!"),
        scope=Scope.settings
    )

    feedback_message = String(
        display_name=_("Feedback message"),
        default=_("Thank you for your feedback!"),
        scope=Scope.settings
    )

    show_aggregate_to_students = Boolean(
        display_name=_("Show aggregate to students"),
        default=False,
        scope=Scope.settings
    )

    @classmethod
    def resource_string(cls, path):
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
        # This is the default prompt if something is not specified in the
        # settings dictionary. Note that this is not the same as the default
        # above. The default above is the prompt the instructor starts from
        # in a tool like Studio. This is a fallback in case some JSON fields
        # are left unpopulated (e.g. if someone manually tweaks the database,
        # in case of OLX authoring, and similar). The examplar above is
        # intended as a well-structured, coherent response. This is designed
        # as generic, to work with any content as a safe fallback.
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
            'icon_set': 'num',
            'placeholder': _("Please take a moment to thoughtfully reflect.")
        }

        prompt.update(self.prompts[index])
        return prompt

    def student_view(self, context=None):  # pylint: disable=unused-argument
        """
        The primary view of the FeedbackXBlock, shown to students
        when viewing courses.
        """
        # Figure out which prompt we show. We set self.prompt_choice to
        # the index of the prompt. We set it if it is out of range (either
        # uninitiailized, or incorrect due to changing list length). Then,
        # we grab the prompt, prepopulated with defaults.
        if self.prompt_choice < 0 or self.prompt_choice >= len(self.prompts):
            self.prompt_choice = random.randint(0, len(self.prompts) - 1)
        prompt = self.get_prompt()

        item_templates_file = "templates/html/scale_item.html"

        # We have five Likert fields right now, but we'd like this to
        # be dynamic
        indexes = range(5)

        # If the user voted before, we'd like to show that
        active_vote = ["checked" if i == self.user_vote else ""
                       for i in indexes]

        # Confirm that we do have vote totals (this may be uninitialized
        # otherwise). This should probably go into __init__ or similar.
        self.init_vote_aggregate()
        votes = self.vote_aggregate

        # We grab the icons. This should move to a Filesystem field so
        # instructors can upload new ones
        def get_url(icon_type, i):
            '''
            Helper function to generate the URL for the icons shown in the
            tool. Takes the type of icon (active, inactive, etc.) and
            the number of the icon.

            Note that some icon types may not be actively used in the
            styling. For example, at the time of this writing, we do
            selected through CSS, rather than by using those icons.
            '''
            templates = {
                'inactive': 'public/default_icons/i{set}{i}.png',
                'active': 'public/default_icons/a{set}{i}.png',
            }
            template = templates[icon_type]
            icon_file = template.format(i=i, set=prompt['icon_set'])
            return self.runtime.local_resource_url(self, icon_file)
        ina_urls = [get_url('inactive', i) for i in range(1, 6)]
        act_urls = [get_url('active', i) for i in range(1, 6)]

        # Prepare the Likert scale fragment to be embedded into the feedback form
        scale = "".join(
            resource_loader.render_django_template(
                item_templates_file,
                {
                    'scale_text': scale_text,
                    'unicode_icon': unicode_icon,
                    'idx': idx,
                    'active': active,
                    'vote_cnt': vote_cnt,
                    'ina_icon': ina_icon,
                    'act_icon': act_icon,
                    'is_display_vote_cnt': self.vote_aggregate and (self.show_aggregate_to_students or self.is_staff()),
                },
                i18n_service=self.runtime.service(self, 'i18n'),
            ) for
            (scale_text,
             unicode_icon,
             idx,
             active,
             vote_cnt,
             act_icon,
             ina_icon,) in
            zip(prompt['scale_text'],
                ICON_SETS[(prompt['icon_set'])],
                indexes,
                active_vote,
                votes,
                act_urls,
                ina_urls)
        )
        if self.user_vote != -1:
            _ = self.runtime.service(self, 'i18n').ugettext
            response = self.voting_message
        else:
            response = ""

        # We initialize self.p_user if not initialized -- this sets whether
        # or not we show it. From there, if it is less than odds of showing,
        # we set the fragment to the rendered XBlock. Otherwise, we return
        # empty HTML. There ought to be a way to return None, but XBlocks
        # doesn't support that.
        if self.p_user == -1:
            self.p_user = random.uniform(0, 100)
        if self.p_user < self.p:
            frag = Fragment()
            frag.add_content(resource_loader.render_django_template(
                'templates/html/feedback.html',
                context={
                    'self': self,
                    'scale': scale,
                    'freeform_prompt': prompt['freeform'],
                    'likert_prompt': prompt['likert'],
                    'response': response,
                    'placeholder': prompt['placeholder']
                },
                i18n_service=self.runtime.service(self, 'i18n')
            ))
        else:
            frag = Fragment('')

        # Finally, we do the standard JS+CSS boilerplate. Honestly, XBlocks
        # ought to have a sane default here.
        frag.add_css(self.resource_string("static/css/feedback.css"))
        frag.add_javascript(self.resource_string("static/js/src/feedback.js"))
        frag.initialize_js('FeedbackXBlock')
        return frag

    def studio_view(self, context):  # pylint: disable=unused-argument
        """
        Create a fragment used to display the edit view in the Studio.
        """
        prompt = self.get_prompt(0)
        for idx in range(len(prompt['scale_text'])):
            prompt['likert{i}'.format(i=idx)] = prompt['scale_text'][idx]
        frag = Fragment()

        prompt.update({
            "display_name": self.display_name,
            "voting_message": self.voting_message,
            "feedback_message": self.feedback_message,
            "show_aggregate_to_students": self.show_aggregate_to_students,
        })
        frag.add_content(resource_loader.render_django_template(
            'templates/html/studio_view.html',
            prompt,
            i18n_service=self.runtime.service(self, 'i18n')
        ))
        js_str = self.resource_string("static/js/src/studio.js")
        frag.add_javascript(six.text_type(js_str))
        frag.initialize_js('FeedbackBlock',
                           {'icon_set': prompt['icon_set']})
        return frag

    @XBlock.json_handler
    def studio_submit(self,
                      data, suffix=''):  # pylint: disable=unused-argument
        """
        Called when submitting the form in Studio.
        """
        for item in ['freeform', 'likert', 'placeholder', 'icon_set']:
            item_submission = data.get(item, None)
            if item_submission and len(item_submission) > 0:
                self.prompts[0][item] = html.escape(item_submission)
        for i in range(5):
            likert = data.get('likert{i}'.format(i=i), None)
            if likert and len(likert) > 0:
                self.prompts[0]['scale_text'][i] = html.escape(likert)

        self.display_name = data.get('display_name')
        self.voting_message = data.get('voting_message')
        self.feedback_message = data.get('feedback_message')
        self.show_aggregate_to_students = data.get("show_aggregate_to_students")

        return {'result': 'success'}

    def init_vote_aggregate(self):
        '''
        There are a lot of places we read the aggregate vote counts. We
        start out with these uninitialized. This guarantees they are
        initialized. We'd prefer to do it this way, rather than default
        value, since we do plan to not force scale length to be 5 in the
        future.
        '''
        if not self.vote_aggregate:
            self.vote_aggregate = [0] * (len(self.get_prompt()['scale_text']))

    def vote(self, data):
        """
        Handle voting
        """
        # prompt_choice is initialized by student view.
        # Ideally, we'd break this out into a function.
        prompt = self.get_prompt(self.prompt_choice)  # pylint: disable=unused-variable]

        # Make sure we're initialized
        self.init_vote_aggregate()

        # Remove old vote if we voted before
        if self.user_vote != -1:
            self.vote_aggregate[self.user_vote] -= 1

        self.user_vote = data['vote']
        self.vote_aggregate[self.user_vote] += 1

    @XBlock.json_handler
    def feedback(self, data, suffix=''):  # pylint: disable=unused-argument
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
                                 'edx.feedbackxblock.nothing_provided',
                                 {})
        if 'vote' in data:
            response = {"success": True,
                        "response": self.voting_message}
            self.runtime.publish(self,
                                 'edx.feedbackxblock.likert_provided',
                                 {'old_vote': self.user_vote,
                                  'new_vote': data['vote']})
            self.vote(data)
        if 'freeform' in data:
            response = {"success": True,
                        "response": self.feedback_message}
            self.runtime.publish(self,
                                 'edx.feedbackxblock.freeform_provided',
                                 {'old_freeform': self.user_freeform,
                                  'new_freeform': data['freeform']})
            self.user_freeform = data['freeform']

        response.update({
            "freeform": self.user_freeform,
            "vote": self.user_vote
        })

        if self.show_aggregate_to_students or self.is_staff():
            response['aggregate'] = self.vote_aggregate

        return response

    @staticmethod
    def workbench_scenarios():
        """
        A canned scenario for display in the workbench.

        We have three blocks. One shows up all the time (for testing). The
        other two show up 50% of the time.
        """
        return [
            ("FeedbackXBlock",
             """<vertical_demo>
                <feedback p="100"/>
                <feedback p="50"/>
                <feedback p="50"/>
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
