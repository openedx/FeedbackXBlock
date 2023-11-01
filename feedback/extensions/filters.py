"""
Open edX Filters needed for instructor dashboard integration.
"""
import pkg_resources
from crum import get_current_request
from django.conf import settings
from django.template import Context, Template
from openedx_filters import PipelineStep
from web_fragments.fragment import Fragment

from feedback.edxapp_wrapper.courseware import get_object_by_usage_id, load_single_xblock
from feedback.edxapp_wrapper.xmodule import modulestore
from feedback.edxapp_wrapper.student_models import CourseEnrollment

TEMPLATE_ABSOLUTE_PATH = "/instructor_dashboard/"
BLOCK_CATEGORY = "feedback_instructor"


class AddFeedbackTab(PipelineStep):
    """Add forum_notifier tab to instructor dashboard."""

    def run_filter(
        self, context, template_name
    ):  # pylint: disable=unused-argument, arguments-differ
        """Execute filter that modifies the instructor dashboard context.
        Args:
            context (dict): the context for the instructor dashboard.
            _ (str): instructor dashboard template name.
        """
        if not settings.FEATURES.get("ENABLE_FEEDBACK_INSTRUCTOR_VIEW", False):
            return {
                "context": context,
            }

        course = context["course"]
        template = Template(self.resource_string(f"static/html/{BLOCK_CATEGORY}.html"))

        request = get_current_request()

        context.update(
            {
                "blocks": load_blocks(request, course),
            }
        )

        html = template.render(Context(context))
        frag = Fragment(html)
        frag.add_css(self.resource_string(f"static/css/{BLOCK_CATEGORY}.css"))
        frag.add_javascript(self.resource_string(f"static/js/src/{BLOCK_CATEGORY}.js"))

        section_data = {
            "fragment": frag,
            "section_key": BLOCK_CATEGORY,
            "section_display_name": "Course Feedback",
            "course_id": str(course.id),
            "template_path_prefix": TEMPLATE_ABSOLUTE_PATH,
        }
        context["sections"].append(section_data)

        return {
            "context": context
        }

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(
            "feedback", path
        )
        return data.decode("utf8")


def load_blocks(request, course):

    course_id = str(course.id)

    feedback_blocks = modulestore().get_items(
        course.id, qualifiers={"category": "feedback"}
    )

    blocks = []
    students = CourseEnrollment.objects.filter(course_id=course_id).values_list("user_id", "user__username")
    for feedback_block in feedback_blocks:
        block = get_object_by_usage_id(
            request, str(course.id), str(feedback_block.location),
            disable_staff_debug_info=True, course=course
        )
        answers = load_xblock_answers(request, students, str(course.location.course_key), str(feedback_block.location), course)

        vote_aggregate = []
        for i, vote in enumerate(block.vote_aggregate):
            vote_aggregate.append({
                "scale_text": block.get_prompt()["scale_text"][i],
                "count": vote,
            })

        blocks.append({
            "display_name": block.display_name,
            "prompts": block.prompts,
            "vote_aggregate": vote_aggregate,
            "answers": answers,
        })
    return blocks


def load_xblock_answers(request, students, course_id, block_id, course):
    """Load answers for a given feedback xblock instance."""
    answers = []
    for user_id, username in students:
        student_xblock_instance = load_single_xblock(request, user_id, course_id, block_id, course)
        if student_xblock_instance:
            prompt = student_xblock_instance.get_prompt()
            answers.append({
                "username": username,
                "user_vote": prompt["scale_text"][student_xblock_instance.user_vote],
                "user_freeform": student_xblock_instance.user_freeform,
            })

    return answers
