from feedback.utils import get_lms_link_for_item
from opaque_keys.edx.keys import UsageKey
from unittest.mock import Mock
import sys
import types


def test_get_lms_link_default(monkeypatch):
    location = Mock(spec=UsageKey)
    location.org = "edX"
    location.course_key = "course-v1:edX+DemoX+2024"
    location.__str__ = lambda self=location: "dummy"

    class MockSiteConfiguration:
        @staticmethod
        def get_value_for_org(org, key, default):
            return default  # simulate missing org-specific config

    monkeypatch.setitem(
        sys.modules,
        "openedx.core.djangoapps.site_configuration.models",
        types.SimpleNamespace(SiteConfiguration=MockSiteConfiguration)
    )

    result = get_lms_link_for_item(location)
    assert result == "https://example.com/courses/course-v1:edX+DemoX+2024/jump_to/dummy"


def test_get_lms_link_with_null_lms_base(monkeypatch):
    location = Mock(spec=UsageKey)
    location.org = "edX"
    location.course_key = "dummy"
    location.__str__ = lambda self=location: "dummy"

    class MockSiteConfiguration:
        @staticmethod
        def get_value_for_org(org, key, default):
            return None  # simulate LMS base not set

    monkeypatch.setitem(
        sys.modules,
        "openedx.core.djangoapps.site_configuration.models",
        types.SimpleNamespace(SiteConfiguration=MockSiteConfiguration)
    )

    result = get_lms_link_for_item(location)
    assert result is None


def test_get_lms_link_with_preview(monkeypatch):
    location = Mock(spec=UsageKey)
    location.org = "edX"
    location.course_key = "course-v1:edX+DemoX+2024"
    location.__str__ = lambda self=location: "dummy"

    class MockSiteConfiguration:
        @staticmethod
        def get_value_for_org(org, key, default):
            return "https://fallback.com"

    monkeypatch.setitem(
        sys.modules,
        "openedx.core.djangoapps.site_configuration.models",
        types.SimpleNamespace(SiteConfiguration=MockSiteConfiguration)
    )

    result = get_lms_link_for_item(location, preview=True)
    assert result == "https://fallback.com/courses/course-v1:edX+DemoX+2024/jump_to/dummy?preview=1"

