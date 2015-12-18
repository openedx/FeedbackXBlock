'''
Tests for the RateXBlock.
'''

import json

from openedx.tests.xblock_integration.xblock_testcase import XBlockTestCase


# pylint: disable=abstract-method
class TestRate(XBlockTestCase):
    """
    Basic tests for the RateXBlock. We set up a page with two
    of the block, make sure the page renders, toggle a few ratings,
    and call it quits.
    """

    olx_scenarios = {  # Currently not used
        "two_rate_block_test_case": """<vertical>
          <rate urlname="rate0"/>
          <rate urlname="rate1"/>
        </vertical>"""
    }

    # This is a stop-gap until we can load OLX and/or OLX from
    # normal workbench scenarios
    test_configuration = [
        {
            "urlname": "two_rate_block_test_case",
            "xblocks": [  # Stopgap until we handle OLX
                {
                    'blocktype': 'rate',
                    'urlname': 'rate_0'
                },
                {
                    'blocktype': 'rate',
                    'urlname': 'rate_1'
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

    def test_rate(self):
        """
        Walk through a few toggles. Make sure the blocks don't mix up
        state between them, initial state is correct, and final state
        is correct.
        """
        # We confirm we don't have errors rendering the student view
        self.check_response('rate_0', 'rate-unset')
        self.check_response('rate_1', 'rate-unset')
        vote_str = 'Thank you for voting!'
        feedback_str = 'Thank you for your feedback!'
        self.submit_feedback('rate_0',
                             {'freeform': 'Worked well', 'vote': 3},
                             {'freeform': 'Worked well', 'vote': 3,
                              'response': vote_str, 'success': True})
        self.submit_feedback('rate_0',
                             {'vote': 4},
                             {'freeform': 'Worked well', 'vote': 4,
                              'response': vote_str, 'success': True})
        self.submit_feedback('rate_0',
                             {'freeform': 'Worked great'},
                             {'freeform': 'Worked great', 'vote': 4,
                              'response': feedback_str, 'success': True})

        # And confirm we render correctly
        self.check_response('rate_0', 'rate-unset')
        self.check_response('rate_1', 'rate-set')
