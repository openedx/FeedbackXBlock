"""Setup for feedback XBlock."""

import os
from setuptools import setup


def package_data(pkg, roots):
    """Generic function to find package_data.

    All of the files under each of the `roots` will be declared as package
    data for package `pkg`.

    """
    data = []
    for root in roots:
        for dirname, _, files in os.walk(os.path.join(pkg, root)):
            for fname in files:
                data.append(os.path.relpath(os.path.join(dirname, fname), pkg))

    return {pkg: data}


setup(
    name='feedback-xblock',
    version='0.0',
    description='XBlock for providing feedback on course content',
    packages=[
        'feedback',
        'feedbacktests'
    ],
    install_requires=[
        'XBlock',
    ],
    entry_points={
        'xblock.v1': [
            'feedback = feedback.feedback:FeedbackXBlock',
        ],
        'xblock.test.v0': [
            'feedbacktest = feedbacktests:TestFeedback',
        ]
    },
    package_data=package_data("feedback", ["static", "public"]),
)
