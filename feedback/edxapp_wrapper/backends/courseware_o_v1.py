"""
Courseware definitions for Open edX Olive release.
"""
from lms.djangoapps.courseware.module_render import get_module_by_usage_id  # pylint: disable=import-error
from lms.djangoapps.courseware.block_render import load_single_xblock  # pylint: disable=import-error


def get_object_by_usage_id(request, course_id, location, disable_staff_debug_info=False, course=None):
    """
    Get the block object for the given block usage id.

    Args:
        request (HttpRequest): Django request object.
        course_id (str): Course ID.
        location (str): block location.
        disable_staff_debug_info (bool): Whether to disable staff debug info.
        course (CourseDescriptor): Course descriptor.

    Returns:
        BlockUsageLocator: Block object.
    """
    block, __ = get_module_by_usage_id(
        request,
        course_id,
        location,
        disable_staff_debug_info=disable_staff_debug_info,
        course=course,
    )
    return block
