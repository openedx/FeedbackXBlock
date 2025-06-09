"""Utilities for feedback app"""

# feedbackblock/feedback/utils.py
from urllib.parse import urlencode, urlparse, urlunparse
from opaque_keys.edx.keys import UsageKey
from django.conf import settings


def _(text):
    """Dummy `gettext` replacement to make string extraction tools scrape strings marked for translation"""
    return text


def get_lms_link_for_item(location, preview=False):
    """
    Returns an LMS link to the course with a jump_to to the provided location.
    """
    assert isinstance(location, UsageKey)

    try:
        from openedx.core.djangoapps.site_configuration.models import SiteConfiguration # pylint: disable=import-outside-toplevel
    except ImportError:
        return None  # or raise a clearer error, or fallback

    lms_base = SiteConfiguration.get_value_for_org(
        location.org,
        "LMS_ROOT_URL",
        settings.LMS_ROOT_URL
    )

    if lms_base is None:
        return None

    query_string = ''
    if preview:
        query_string = urlencode({'preview': '1'})

    url_parts = list(urlparse(lms_base))
    url_parts[2] = f'/courses/{location.course_key}/jump_to/{location}'
    url_parts[4] = query_string

    return urlunparse(url_parts)
