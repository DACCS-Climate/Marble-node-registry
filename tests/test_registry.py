import os

import json
import jsonschema
import pytest


@pytest.fixture(autouse=True)
def links_json_schema(requests_mock, request):
    """
    Mock the `requests.get` call to the json-schema links hyper-schema so that these tests can be run offline if needed.
    """
    this_dir = os.path.dirname(request.fspath)
    with open(os.path.join(this_dir, "fixtures", "links-schema-cache.json")) as f:
        content = f.read()
    requests_mock.get("https://json-schema.org/draft/2020-12/links", text=content)


@pytest.fixture
def registry_content(request):
    """Return the content contained in node_registry.json"""
    root_dir = os.path.dirname(os.path.dirname(request.fspath))
    example_registry = os.path.join(root_dir, "node_registry.json")
    with open(example_registry) as f:
        content = json.load(f)
    return content


@pytest.fixture
def schema_content(request):
    """Return the content contained in node_registry.schema.json"""
    root_dir = os.path.dirname(os.path.dirname(request.fspath))
    example_schema = os.path.join(root_dir, "node_registry.schema.json")
    with open(example_schema) as f:
        content = json.load(f)
    return content


def test_valid_registry(registry_content, schema_content):
    jsonschema.validate(registry_content, schema_content)
