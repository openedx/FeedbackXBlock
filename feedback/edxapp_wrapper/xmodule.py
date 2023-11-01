"""
Xmodule generalized definitions.
"""

from importlib import import_module
from django.conf import settings


def get_modulestore_function(*args, **kwargs):
    """Get modulestore object."""

    backend_function = settings.FEEDBACK_XMODULE_BACKEND
    backend = import_module(backend_function)

    return backend.get_modulestore(*args, **kwargs)


modulestore = get_modulestore_function
