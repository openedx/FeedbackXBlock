"""
Test settings for the Feedback XBlock.
"""

from workbench.settings import *

from django.conf.global_settings import LOGGING

INSTALLED_APPS = [
'django.contrib.admin',
'django.contrib.auth',
'django.contrib.contenttypes',
'workbench',
]
