'''
Tests for the FeedbackXBlock.
'''

import json

from openedx.tests.xblock_integration.xblock_testcase import XBlockTestCase


class PatchRandomMixin:
    """
    This is a class which will patch random.uniform so that we can
    confirm whether randomization works.
    """
    def setUp(self):
        self.value = None

        def patched_uniform(mock_self, min, max):
            return self.value

        patcher = mock.patch("random.random.uniform",
                             patched_uniform)
        patcher.start()
        self.addCleanup(patcher.stop)

    def set_random(self, value):
        self.value = value


# pylint: disable=abstract-method
class TestFeedback(XBlockTestCase):
    """
    Basic tests for the FeedbackXBlock. We set up a page with two
    of the block, make sure the page renders, toggle a few ratings,
    and call it quits.
    """

    olx_scenarios = {  # Currently not used
        "two_feedback_block_test_case": """<vertical>
          <feedback urlname="feedback0"/>
          <feedback urlname="feedback1"/>
        </vertical>"""
    }

    # This is a stop-gap until we can load OLX and/or OLX from
    # normal workbench scenarios
    test_configuration = [
        {
            "urlname": "two_feedback_block_test_case",
            "xblocks": [  # Stopgap until we handle OLX
                {
                    'blocktype': 'feedback',
                    'urlname': 'feedback_0',
                    'parameters': {'p': 100}
                },
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
        print json.dumps(resp.data, indent=2)
        print json.dumps(desired_state, indent=2)
        # pylint: disable=no-member
        self.assertEqual(resp.data, desired_state)

    # pylint: disable=unused-argument
    def check_response(self, block_urlname, rendering):
        """
        Confirm that we have a 200 response code (no server error)

        In the future, visual diff test the response.
        """
        response = self.render_block(block_urlname)
        self.assertEqual(response.status_code, 200)
        # To do: Below method needs to be implemented
        # self.assertXBlockScreenshot(block_urlname, rendering)

    def test_feedback(self):
        """
        Walk through a few toggles. Make sure the blocks don't mix up
        state between them, initial state is correct, and final state
        is correct.
        """
        # We confirm we don't have errors rendering the student view
        self.check_response('feedback_0', 'feedback-unset')
        self.check_response('feedback_1', 'feedback-unset')
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
        self.check_response('feedback_0', 'feedback-unset')
        self.check_response('feedback_1', 'feedback-set')
