import pytest
from mock import Mock

from workbench.runtime import WorkbenchRuntime
from xblock.fields import ScopeIds
from xblock.runtime import DictKeyValueStore, KvsFieldData

from feedback.feedback import FeedbackXBlock


def generate_scope_ids(runtime, block_type):
    """ helper to generate scope IDs for an XBlock """
    def_id = runtime.id_generator.create_definition(block_type)
    usage_id = runtime.id_generator.create_usage(def_id)
    return ScopeIds('user', block_type, def_id, usage_id)


@pytest.fixture
def feedback_xblock():
    """Feedback XBlock pytest fixture."""
    runtime = WorkbenchRuntime()
    key_store = DictKeyValueStore()
    db_model = KvsFieldData(key_store)
    ids = generate_scope_ids(runtime, 'feedback')
    feedback_xblock = FeedbackXBlock(runtime, db_model, scope_ids=ids)
    feedback_xblock.usage_id = Mock()
    return feedback_xblock
