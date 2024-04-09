import copy
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
def registry_content_with_services(registry_content):
    any_svc_key = list(registry_content)[0]
    registry_content["test"] = copy.deepcopy(registry_content[any_svc_key])
    registry_content["test"]["services"] = [
        {
            "name": "test-service",
            "keywords": ["other"],
            "description": "test service",
            "version": "1.2.3",
            "links": [
                {
                    "rel": "service",
                    "href": "https://example.com/test",
                    "type": "application/json"
                },
                {
                    "rel": "service-doc",
                    "href": "https://readthedocs.com/example",
                    "type": "text/html"
                }
            ]
        }
    ]
    return registry_content


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


def test_services_good_version(registry_content_with_services, schema_content):
    jsonschema.validate(registry_content_with_services, schema_content)


def test_services_bad_version(registry_content_with_services, schema_content):
    registry_content_with_services["test"]["services"][0]["version"] = "bad_version"
    with pytest.raises(jsonschema.exceptions.ValidationError) as exc:
        jsonschema.validate(registry_content_with_services, schema_content)
    assert "bad_version" in exc.value.message
    assert list(exc.value.path) == ["test", "services", 0, "version"]
    assert list(exc.value.schema_path)[-6:] == ["properties", "services", "items", "properties", "version", "pattern"]


def test_services_bad_links(registry_content_with_services, schema_content):
    registry_content_with_services["test"]["services"][0].pop("links")
    with pytest.raises(jsonschema.exceptions.ValidationError) as exc:
        jsonschema.validate(registry_content_with_services, schema_content)
    assert exc.value.message == "'links' is a required property"
    assert list(exc.value.path) == ["test", "services", 0]
    assert list(exc.value.schema_path)[-4:] == ["properties", "services", "items", "required"]


@pytest.mark.parametrize(
    ["required_link_rel", "expected_link_pos"],
    [
        ("service", 0),
        ("service-doc", 1),
    ]
)
def test_services_missing_link(registry_content_with_services, schema_content, required_link_rel, expected_link_pos):
    links = registry_content_with_services["test"]["services"][0]["links"]
    links = [link for link in links if link["rel"] != required_link_rel]
    registry_content_with_services["test"]["services"][0]["links"] = links
    with pytest.raises(jsonschema.exceptions.ValidationError) as exc:
        jsonschema.validate(registry_content_with_services, schema_content)
    assert "does not contain" in exc.value.message
    assert list(exc.value.path) == ["test", "services", 0, "links"]
    assert list(exc.value.schema_path)[-4:] == ["links", "allOf", expected_link_pos, "contains"]
