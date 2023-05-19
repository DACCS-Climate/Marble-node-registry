import pytest
from daccs_node_registry import update


@pytest.fixture(autouse=True)
def updated_registry(mocker):
    yield mocker.patch.object(update, "_write_registry")


@pytest.fixture
def patched_registry(mocker):
    yield mocker.patch.object(update, "_load_registry")


def test_empty_registry_does_nothing(patched_registry, updated_registry):
    patched_registry.return_value = {}
    update.update_registry()
    assert updated_registry.call_args.args == ({},)


