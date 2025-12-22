"""
Common Test settings for eox_hooks project.
For more information on this file, see
https://docs.djangoproject.com/en/2.22/topics/settings/
For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.22/ref/settings/
"""
from workbench.settings import *  # pylint: disable=wildcard-import

from django.conf.global_settings import LOGGING

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'feedback',
    'workbench',
]

FEATURES = {
    "ENABLE_FEEDBACK_INSTRUCTOR_VIEW": True,
}

SECRET_KEY = 'fake-key'

LMS_ROOT_URL = "https://example.com"
