'''
Tests for the FeedbackXBlock.
'''

import json
import sys

from openedx.tests.xblock_integration.xblock_testcase import XBlockTestCase
import mock


class PatchRandomMixin(object):
    """
    This is a class which will patch random.uniform so that we can
    confirm whether randomization works.
    """
    def setUp(self):
        super(PatchRandomMixin, self).setUp()
        self.random_patch_value = None

        def patched_uniform(min, max):
            return self.random_patch_value

        patcher = mock.patch("feedback.feedback.random.uniform",
                             patched_uniform)
        patcher.start()
        self.addCleanup(patcher.stop)

    def set_random(self, random_patch_value):
        self.random_patch_value = random_patch_value


# pylint: disable=abstract-method
class TestFeedback(PatchRandomMixin, XBlockTestCase):
    """
    Basic tests for the FeedbackXBlock. We set up a page with two
    of the block, make sure the page renders, toggle a few ratings,
    and call it quits.
    """

    olx_scenarios = {  # Currently not used
        "two_feedback_block_test_case": """<vertical>
          <feedback urlname="feedback_0" p="100"/>
          <feedback urlname="feedback_1" p="50"/>
        </vertical>"""
    }

    # This is a stop-gap until we can load OLX and/or OLX from
    # normal workbench scenarios
    test_configuration = [
        {
            "urlname": "feedback_block_test_case_0",
            "xblocks": [  # Stopgap until we handle OLX
                {
                    'blocktype': 'feedback',
                    'urlname': 'feedback_0',
                    'parameters': {'p': 100}
                }
            ]
        },
        {
            "urlname": "feedback_block_test_case_1",
            'xblocks': [
                {
                    'blocktype': 'feedback',
                    'urlname': 'feedback_1',
                    'parameters': {'p': 50}
                }
            ]
        }
    ]

    def submit_feedback(self, block, data, desired_state):
        """
        Make an AJAX call to the XBlock, and assert the state is as
        desired.
        """
        resp = self.ajax('feedback', block, data)
        self.assertEqual(resp.status_code, 200)
        # pylint: disable=no-member
        self.assertEqual(resp.data, desired_state)

    # pylint: disable=unused-argument
    def check_response(self, block_urlname, rendered):
        """
        Confirm that we have a 200 response code (no server error)

        Confirm that we do this stochastically based no `p`
        """
        response = self.render_block(block_urlname)
        self.assertEqual(response.status_code, 200)
        if rendered:
            self.assertTrue('feedback_likert_scale' in response.content)
        else:
            self.assertFalse('feedback_likert_scale' in response.content)

    def test_feedback(self):
        """
        Walk through a few ratings. Make sure the blocks don't mix up
        state between them, initial state is correct, and final state
        is correct.
        """
        self.select_student(0)
        # We confirm we don't have errors rendering the student view
        self.check_response('feedback_0', True)
        # At 45, feedback_1 should render
        self.set_random(45)
        self.check_response('feedback_1', True)
        vote_str = 'Thank you for voting!'
        feedback_str = 'Thank you for your feedback!'
        self.submit_feedback('feedback_0',
                             {'freeform': 'Worked well', 'vote': 3},
                             {'freeform': 'Worked well', 'vote': 3,
                              'response': feedback_str, 'success': True})
        self.submit_feedback('feedback_0',
                             {'vote': 4},
                             {'freeform': 'Worked well', 'vote': 4,
                              'response': vote_str, 'success': True})
        self.submit_feedback('feedback_0',
                             {'freeform': 'Worked great'},
                             {'freeform': 'Worked great', 'vote': 4,
                              'response': feedback_str, 'success': True})
        # And confirm we render correctly
        self.check_response('feedback_0', True)
        # Feedback 1 should render again; this should be stored in a
        # field
        self.set_random(55)
        self.check_response('feedback_1', True)

        # But it should not render for a new student
        self.select_student(1)
        self.check_response('feedback_1', False)
