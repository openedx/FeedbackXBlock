"""
Test for the instructor dashboard filters.
"""

from unittest import TestCase
from unittest.mock import Mock, patch
from django.test.utils import override_settings


from feedback.extensions.filters import AddFeedbackTab, load_xblock_answers

class TestFilters(TestCase):
    """
    Test suite for the FeedbackXBlock filters.
    """

    def setUp(self) -> None:
        """
        Set up the test suite.
        """
        self.filter = AddFeedbackTab(filter_type=Mock(), running_pipeline=Mock())

    @patch("feedback.extensions.filters.get_user_enrollments")
    @patch("feedback.extensions.filters.get_block_by_usage_id")
    @patch("feedback.extensions.filters.modulestore")
    def test_run_filter_without_blocks(self, modulestore_mock, get_block_by_usage_id_mock, get_user_enrollments_mock):
        """
        Check the filter is not executed when there are no Feedback blocks in the course.

        Expected result:
            - The context is returned without modifications.
        """
        modulestore_mock().get_items.return_value = []
        context = {"course": Mock(id="test-course-id"), "sections": []}
        template_name = "test-template-name"

        self.filter.run_filter(context, template_name)

        get_block_by_usage_id_mock.assert_not_called()
        get_user_enrollments_mock.assert_not_called()


    @patch("feedback.extensions.filters.get_lms_link_for_item")
    @patch("feedback.extensions.filters.get_user_enrollments")
    @patch("feedback.extensions.filters.get_block_by_usage_id")
    @patch("feedback.extensions.filters.load_single_xblock")
    @patch("feedback.extensions.filters.modulestore")
    def test_run_filter(self, modulestore_mock, load_single_xblock_mock, get_block_by_usage_id_mock, get_user_enrollments_mock,
                        get_lms_link_for_item_mock):
        """
        Check the filter is executed when there are Feedback blocks in the course.

        Expected result:
            - The context is returned with the Feedback blocks information.
        """
        modulestore_mock().get_items.return_value = [Mock(location="test-location")]
        context = {"course": Mock(id="test-course-id"), "sections": []}
        template_name = "test-template-name"
        get_user_enrollments_mock.value_list = [(1, "test-username")]
        block_mock = Mock(
            vote_aggregate=[],
        )
        block_mock.get_prompt.return_value = {"scale_text": ["test-scale-text"]}
        get_block_by_usage_id_mock.return_value = block_mock, None
        get_lms_link_for_item_mock.return_value = "test-url"
        load_single_xblock_mock.return_value = Mock(
            user_vote=1,
            user_freeform="test-user-freeform",
        )

        result = self.filter.run_filter(context, template_name)

        get_block_by_usage_id_mock.assert_called()
        get_user_enrollments_mock.assert_called_once()
        self.assertEqual(1, len(result.get("context", {})["sections"]))

    @override_settings(
        FEATURES={"ENABLE_FEEDBACK_INSTRUCTOR_VIEW":False}
    )
    def test_run_filter_disable(self):
        context = {"course": Mock(id="test-course-id"), "sections": []}
        template_name = "test-template-name"

        new_context = self.filter.run_filter(context, template_name)["context"]

        self.assertEqual(context, new_context)

    @patch("feedback.extensions.filters.load_single_xblock")
    def test_load_xblock_answers(self, load_single_xblock_mock):
        request_mock = Mock()
        students = [(1, "test-username")]
        course_id = "test-course-id"
        block_id = "test-block-id"
        course = Mock()

        single_block = Mock(
            user_vote=0,
            user_freeform="test-user-freeform",
        )
        single_block.get_prompt.return_value = {"scale_text": ["test-scale-text"]}

        load_single_xblock_mock.return_value = single_block

        answers = load_xblock_answers(request_mock, students, course_id, block_id, course)

        self.assertEqual(
            [
                {
                    "username": "test-username",
                    "user_vote": "test-scale-text",
                    "user_freeform": "test-user-freeform",
                }
            ],
            answers,
        )


    @patch("feedback.extensions.filters.load_single_xblock")
    def test_load_xblock_answers_skip_empty(self, load_single_xblock_mock):
        request_mock = Mock()
        students = [(1, "test-username")]
        course_id = "test-course-id"
        block_id = "test-block-id"
        course = Mock()

        single_block = Mock(
            user_vote=-1,
            user_freeform="",
        )
        single_block.get_prompt.return_value = {"scale_text": ["test-scale-text"]}

        load_single_xblock_mock.return_value = single_block

        answers = load_xblock_answers(request_mock, students, course_id, block_id, course)

        self.assertEqual(
            [],
            answers,
        )
