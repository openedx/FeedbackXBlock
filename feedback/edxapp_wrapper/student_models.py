"""
Courseware generalized definitions.
"""

from importlib import import_module
from django.conf import settings


def get_course_enrollment_model(*args, **kwargs):
    """Get the block object for the given block usage id."""

    backend_function = settings.FEEDBACK_COURSE_ENROLLMENT_MODEL_BACKEND
    backend = import_module(backend_function)

    return backend.CourseEnrollment


CourseEnrollment = get_course_enrollment_model()
