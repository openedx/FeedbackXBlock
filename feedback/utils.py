"""Utilities for feedback app"""

# feedbackblock/feedback/utils.py
from urllib.parse import urlencode, urlparse, urlunparse
from opaque_keys.edx.keys import UsageKey
from django.conf import settings
from openedx.core.djangoapps.site_configuration.models import SiteConfiguration


def _(text):
    """Dummy `gettext` replacement to make string extraction tools scrape strings marked for translation"""
    return text


def get_lms_link_for_item(location, preview=False):
    """
    Returns an LMS link to the course with a jump_to to the provided location.
    """
    assert isinstance(location, UsageKey)

    lms_base = SiteConfiguration.get_value_for_org(
        location.org,
        "LMS_ROOT_URL",
        settings.LMS_ROOT_URL
    )
    query_string = ''

    if lms_base is None:
        return None

    if preview:
        query_string = urlencode({'preview': '1'})

    url_parts = list(urlparse(lms_base))
    url_parts[2] = '/courses/{course_key}/jump_to/{location}'.format(
        course_key=str(location.course_key),
        location=str(location),
    )
    url_parts[4] = query_string

    return urlunparse(url_parts)
