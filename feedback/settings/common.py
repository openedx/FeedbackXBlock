"""
Common Django settings for eox_hooks project.
For more information on this file, see
https://docs.djangoproject.com/en/2.22/topics/settings/
For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.22/ref/settings/
"""
from feedback import ROOT_DIRECTORY

INSTALLED_APPS = [
    "feedback",
]


def plugin_settings(settings):
    """
    Set of plugin settings used by the Open Edx platform.
    More info: https://github.com/edx/edx-platform/blob/master/openedx/core/djangoapps/plugins/README.rst
    """
    settings.MAKO_TEMPLATE_DIRS_BASE.append(ROOT_DIRECTORY / "templates")

    # Backend settings
    settings.FEEDBACK_COURSEWARE_BACKEND = "feedback.edxapp_wrapper.backends.courseware_p_v1"
    settings.FEEDBACK_XMODULE_BACKEND = "feedback.edxapp_wrapper.backends.xmodule_p_v1"
    settings.FEEDBACK_COURSE_ENROLLMENT_MODEL_BACKEND = "feedback.edxapp_wrapper.backends.student_models_p_v1"
