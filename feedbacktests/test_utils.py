from feedback.utils import get_lms_link_for_item
from opaque_keys.edx.keys import UsageKey
from unittest.mock import Mock


def test_get_lms_link_default(monkeypatch):
    location = Mock(spec=UsageKey)
    location.org = "edX"
    location.course_key = "course-v1:edX+DemoX+2024"
    location.__str__ = lambda self=location: "dummy"

    class MockSettings:
        LMS_ROOT_URL = "https://example.com"
    monkeypatch.setattr("feedback.utils.settings", MockSettings)

    class MockSiteConfiguration:
        @staticmethod
        def get_value_for_org(org, key, default):
            return default  # simulate missing config
    monkeypatch.setitem(
        __import__("sys").modules,
        "openedx.core.djangoapps.site_configuration.models",
        __import__("types").SimpleNamespace(
            SiteConfiguration=MockSiteConfiguration))

    result = get_lms_link_for_item(location)
    assert result == "https://example.com/courses/course-v1:edX+DemoX+2024/jump_to/dummy"
