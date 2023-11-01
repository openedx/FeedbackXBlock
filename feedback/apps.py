"""
forum_email_notifier Django application initialization.
"""

from django.apps import AppConfig


class FeedbackConfig(AppConfig):
    """
    Configuration for the feedback Django application.
    """

    name = "feedback"

    plugin_app = {
        "settings_config": {
            "lms.djangoapp": {
                "common": {"relative_path": "settings.common"},
                "test": {"relative_path": "settings.test"},
                "production": {"relative_path": "settings.production"},
            },
            "cms.djangoapp": {
                "common": {"relative_path": "settings.common"},
                "test": {"relative_path": "settings.test"},
                "production": {"relative_path": "settings.production"},
            },
        },
    }

    def ready(self):
        """
        Perform initialization tasks required for the forum_email_notifier Django application.
        """
        super().ready()
        from feedback.extensions import (  # noqa pylint: disable=unused-import, import-outside-toplevel
            filters,
        )
