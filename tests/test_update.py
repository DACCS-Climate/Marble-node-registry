import json
import os
from copy import deepcopy

import pytest

import update # type: ignore

GOOD_SERVICES = {
    "services": [
        {
            "name": "geoserver",
            "types": ["data", "wps", "wms", "wfs"],
            "keywords": ["data", "service-wps", "service-wms", "service-wfs"],
            "description": "GeoServer is a server that allows users to view and edit geospatial data.",
            "links": [
                {"rel": "service", "type": "application/json", "href": "https://daccs-uoft.example.com/geoserver/"},
                {"rel": "service-doc", "type": "text/html", "href": "https://docs.geoserver.org/"},
            ],
        },
        {
            "name": "weaver",
            "types": ["ogcapi_processes"],
            "keywords": ["service-ogcapi_processes", "some-other-keyword"],
            "description": "An OGC-API flavored Execution Management Service",
            "links": [
                {"rel": "service", "type": "application/json", "href": "https://daccs-uoft.example.com/weaver/"},
                {"rel": "service-doc", "type": "text/html", "href": "https://pavics-weaver.readthedocs.io/"},
                {
                    "rel": "http://www.opengis.net/def/rel/ogc/1.0/conformance",
                    "type": "application/json",
                    "href": "https://example.com/weaver/conformance/",
                },
            ],
        },
    ]
}


@pytest.fixture(autouse=True)
def updated_registry(mocker):
    """Mock the _write_registry function so that nothing is actually written to disk during the tests run"""
    yield mocker.patch.object(update, "_write_registry")


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
def patched_registry(mocker):
    """Mock the _load_registry function so that the original registry content can be manipulated for the test"""
    yield mocker.patch.object(update, "_load_registry")


@pytest.fixture
def example_registry_content(request):
    """Return the content contained in ../doc/node_registry.example.json"""
    root_dir = os.path.dirname(os.path.dirname(request.fspath))
    example_registry = os.path.join(root_dir, "doc", "node_registry.example.json")
    with open(example_registry) as f:
        content = json.load(f)
    return content


@pytest.fixture
def example_initial_registry_content(example_registry_content):
    """
    Return the content contained in ../doc/node_registry.example.json without the content that would not be updated
    until the first update has run
    """
    for key in example_registry_content:
        data = example_registry_content[key]
        data.pop("services")
        data.pop("last_updated")
        data.pop("version")
        data.pop("status")
    return example_registry_content


@pytest.fixture
def example_initial_registry(patched_registry, example_initial_registry_content):
    """
    Return a patched version of the _load_registry function that returns the content of
    example_initial_registry_content
    """
    patched_registry.return_value = deepcopy(example_initial_registry_content)
    return patched_registry


@pytest.fixture
def example_registry(patched_registry, example_registry_content):
    """Return a patched version of the _load_registry function that returns the content of example_registry_content"""
    patched_registry.return_value = deepcopy(example_registry_content)
    return patched_registry


@pytest.fixture
def example_node_name(example_registry_content):
    """Return the name of the node in example_registry_content"""
    return list(example_registry_content)[0]


class TestEmptyRegistry:
    """Test when the registry is initially empty"""

    @pytest.fixture(autouse=True)
    def setup(self, patched_registry):
        patched_registry.return_value = {}
        update.update_registry()

    def test_nothing_updated(self, updated_registry):
        """Test that the registry did not change"""
        assert updated_registry.call_args.args == ({},)


class TestOfflineNode:
    """Test when the node is offline (unavailable over the network)"""

    @pytest.fixture(autouse=True)
    def setup(self, mocker, example_registry):
        mocker.patch.object(update.requests, "get").side_effect = update.requests.exceptions.ConnectionError("message")
        update.update_registry()

    def test_status_offline(self, example_node_name, example_registry_content, updated_registry):
        """Test that the status is set to 'offline'"""
        assert updated_registry.call_args.args[0][example_node_name]["status"] == "offline"

    def test_services_no_change(self, example_node_name, example_registry_content, updated_registry):
        """Test that the services values did not change"""
        assert (
            updated_registry.call_args.args[0][example_node_name]["services"]
            == example_registry_content[example_node_name]["services"]
        )

    def test_version_no_change(self, example_node_name, example_registry_content, updated_registry):
        """Test that the version value did not change"""
        assert (
            updated_registry.call_args.args[0][example_node_name]["version"]
            == example_registry_content[example_node_name]["version"]
        )

    def test_last_updated_no_change(self, example_node_name, example_registry_content, updated_registry):
        """Test that the last_updated did not change"""
        assert (
            updated_registry.call_args.args[0][example_node_name]["last_updated"]
            == example_registry_content[example_node_name]["last_updated"]
        )


class TestNodeReturnsInvalidJson:
    """Test when the /services route returns a string that is not parseable as valid json"""

    @pytest.fixture(autouse=True)
    def setup(self, example_node_name, example_registry, example_registry_content, requests_mock):
        services_url = next(
            link["href"] for link in example_registry_content[example_node_name]["links"] if link["rel"] == "collection"
        )
        version_url = next(
            link["href"] for link in example_registry_content[example_node_name]["links"] if link["rel"] == "version"
        )
        requests_mock.get(services_url, text='{"a":')
        requests_mock.get(version_url, text="1.2.3")
        update.update_registry()

    def test_status_unresponsive(self, example_node_name, example_registry_content, updated_registry):
        """Test that the status is updated to 'unresponsive'"""
        assert updated_registry.call_args.args[0][example_node_name]["status"] == "unresponsive"

    def test_services_no_change(self, example_node_name, example_registry_content, updated_registry):
        """Test that the services values did not change"""
        assert (
            updated_registry.call_args.args[0][example_node_name]["services"]
            == example_registry_content[example_node_name]["services"]
        )

    def test_version_no_change(self, example_node_name, example_registry_content, updated_registry):
        """Test that the version value did not change"""
        assert (
            updated_registry.call_args.args[0][example_node_name]["version"]
            == example_registry_content[example_node_name]["version"]
        )

    def test_last_updated_no_change(self, example_node_name, example_registry_content, updated_registry):
        """Test that the last_updated value did not change"""
        assert (
            updated_registry.call_args.args[0][example_node_name]["last_updated"]
            == example_registry_content[example_node_name]["last_updated"]
        )


class InitialTests:
    """Abstract test class used to test when no updates have previously been run"""

    services: dict
    version: dict = {"version": "1.2.3"}

    @pytest.fixture(autouse=True)
    def setup(self, example_node_name, example_initial_registry, example_registry_content, requests_mock):
        services_url = next(
            link["href"] for link in example_registry_content[example_node_name]["links"] if link["rel"] == "collection"
        )
        version_url = next(
            link["href"] for link in example_registry_content[example_node_name]["links"] if link["rel"] == "version"
        )
        services = deepcopy(self.services)
        for s in services.values():
            if isinstance(s, dict) and "date_added" in s:
                s.pop("date_added")
        requests_mock.get(services_url, json=self.services)
        requests_mock.get(version_url, json=self.version)
        update.update_registry()


class NonInitialTests:
    """Abstract test class used to test when updates have previously been run"""

    services: dict
    version: dict = {"version": "1.2.3"}

    @pytest.fixture(autouse=True)
    def setup(self, example_node_name, example_registry, example_registry_content, requests_mock):
        services_url = next(
            link["href"] for link in example_registry_content[example_node_name]["links"] if link["rel"] == "collection"
        )
        version_url = next(
            link["href"] for link in example_registry_content[example_node_name]["links"] if link["rel"] == "version"
        )
        requests_mock.get(services_url, json=self.services)
        requests_mock.get(version_url, json=self.version)
        update.update_registry()


class ValidResponseTests:
    """Abstract test class used to test when the updates are expected to complete successfully for all nodes"""

    services: dict
    version: dict

    def test_status_online(self, example_node_name, updated_registry):
        """Test that the status is updated to 'online'"""
        assert updated_registry.call_args.args[0][example_node_name]["status"] == "online"

    def test_services_updated(self, example_node_name, updated_registry):
        """Test that the services values are updated"""
        assert updated_registry.call_args.args[0][example_node_name]["services"] == self.services["services"]

    def test_version_updated(self, example_node_name, updated_registry):
        """Test that the version value is updated"""
        assert updated_registry.call_args.args[0][example_node_name]["version"] == self.version["version"]

    def test_last_updated_updated(self, example_node_name, example_registry_content, updated_registry):
        """Test that the last_updated value is updated"""
        assert updated_registry.call_args.args[0][example_node_name]["last_updated"] != example_registry_content[
            example_node_name
        ].get("last_updated")


class InvalidResponseTests:
    """
    Abstract test class used to test when the updates are not expected to complete successfully for all nodes because
    resulting registry content is invalid according to the json schema
    """

    services: dict
    version: dict

    def test_status_invalid_configuration(self, example_node_name, updated_registry):
        """Test that the status is updated to 'invalid_configuration'"""
        assert updated_registry.call_args.args[0][example_node_name]["status"] == "invalid_configuration"

    def test_services_no_change(self, example_node_name, example_registry_content, updated_registry):
        """Test that the services values are not updated"""
        assert updated_registry.call_args.args[0][example_node_name].get("services") == example_registry_content[
            example_node_name
        ].get("services")

    def test_version_no_change(self, example_node_name, example_registry_content, updated_registry):
        """Test that the version value is not updated"""
        assert updated_registry.call_args.args[0][example_node_name].get("version", {}) == example_registry_content[
            example_node_name
        ].get("version", {})

    def test_last_updated_no_change(self, example_node_name, example_registry_content, updated_registry):
        """Test that the last_updated value is not updated"""
        assert updated_registry.call_args.args[0][example_node_name].get("last_updated") == example_registry_content[
            example_node_name
        ].get("last_updated")


class TestInitialUpdateNoServices(ValidResponseTests, InitialTests):
    """Test when no updates have previously been run and there are no reported services"""

    services = {"services": []}


class TestInitialUpdateInvalidServices(InvalidResponseTests, InitialTests):
    """
    Test when no updates have previously been run and the reported services are invalid according to the json schema
    """

    services = {"services": [{"bad_key": "some_value"}]}


class TestOnlineNodeInitialUpdateWithValidServicesAndVersion(ValidResponseTests, InitialTests):
    """Test when no updates have previously been run and the reported services and version are valid"""

    services = GOOD_SERVICES


class TestOnlineNodeInitialUpdateWithInvalidVersion(InvalidResponseTests, InitialTests):
    """Test when no updates have previously been run and the reported version is not valid"""

    services = GOOD_SERVICES
    version = {"version": "abc123"}


class TestOnlineNodeUpdateWithValidServicesAndVersion(ValidResponseTests, NonInitialTests):
    """Test when updates have previously been run and the reported services and version are valid"""

    services = GOOD_SERVICES


class TestOnlineNodeUpdateWithInvalidVersion(InvalidResponseTests, NonInitialTests):
    """Test when updates have previously been run and the reported version is not valid"""

    services = GOOD_SERVICES
    version = {"version": "abc123"}


class TestOnlineNodeUpdateWithInvalidServices(InvalidResponseTests, NonInitialTests):
    """Test when updates have previously been run and the reported services are not valid"""

    services = {"services": [{"bad_key": "some_value"}]}


class TestOnlineNodeUpdateWithInvalidServiceTypes(InvalidResponseTests, NonInitialTests):
    """Test when updates have previously been run and the reported services types are not valid"""

    services = deepcopy(GOOD_SERVICES)

    @pytest.fixture(scope="class", autouse=True)
    def bad_types(self):
        self.services["services"][0]["types"] = ["something-bad"]


class TestOnlineNodeUpdateWithNoTypes(ValidResponseTests, NonInitialTests):
    """
    Test when updates have previously been run and there are no services types

    This ensures that service types are updated as expected from the provided keywords
    """

    services = deepcopy(GOOD_SERVICES)

    @pytest.fixture(scope="class", autouse=True)
    def no_types(self):
        for service in self.services["services"]:
            service.pop("types")

    def test_services_updated(self, example_node_name, updated_registry):
        """Test that the services values are updated"""
        assert updated_registry.call_args.args[0][example_node_name]["services"] == GOOD_SERVICES["services"]
