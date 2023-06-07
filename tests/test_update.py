import os
import json
from copy import deepcopy

import pytest
from daccs_node_registry import update


@pytest.fixture(autouse=True)
def updated_registry(mocker):
    """Mock the _write_registry function so that nothing is actually written to disk during the tests run"""
    yield mocker.patch.object(update, "_write_registry")


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
        requests_mock.get(os.path.join(example_registry_content[example_node_name]["url"], "services"), text='{"a":')
        requests_mock.get(os.path.join(example_registry_content[example_node_name]["url"], "version"), text="1.2.3")
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
        requests_mock.get(
            os.path.join(example_registry_content[example_node_name]["url"], "services"), json=self.services
        )
        requests_mock.get(
            os.path.join(example_registry_content[example_node_name]["url"], "version"), json=self.version
        )
        update.update_registry()


class NonInitialTests:
    """Abstract test class used to test when updates have previously been run"""

    services: dict
    version: dict = {"version": "1.2.3"}

    @pytest.fixture(autouse=True)
    def setup(self, example_node_name, example_registry, example_registry_content, requests_mock):
        requests_mock.get(
            os.path.join(example_registry_content[example_node_name]["url"], "services"), json=self.services
        )
        requests_mock.get(
            os.path.join(example_registry_content[example_node_name]["url"], "version"), json=self.version
        )
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

    services = {
        "services": [
            {
                "url": "http://example.com",
                "name": "thredds",
                "type": ["data"],
                "documentation": "http://doc.example.com",
                "description": "service description",
            }
        ]
    }


class TestOnlineNodeInitialUpdateWithInvalidVersion(InvalidResponseTests, InitialTests):
    """Test when no updates have previously been run and the reported version is not valid"""

    services = {
        "services": [
            {
                "url": "http://example.com",
                "name": "thredds",
                "type": ["data"],
                "documentation": "http://doc.example.com",
                "description": "service description",
            }
        ]
    }
    version = {"version": "abc123"}


class TestOnlineNodeUpdateWithValidServicesAndVersion(ValidResponseTests, NonInitialTests):
    """Test when updates have previously been run and the reported services and version are valid"""

    services = {
        "services": [
            {
                "url": "http://example.com",
                "name": "thredds",
                "type": ["data"],
                "documentation": "http://doc.example.com",
                "description": "service description",
            }
        ]
    }


class TestOnlineNodeUpdateWithInvalidVersion(InvalidResponseTests, NonInitialTests):
    """Test when updates have previously been run and the reported version is not valid"""

    services = {
        "services": [
            {
                "url": "http://example.com",
                "name": "thredds",
                "type": ["data"],
                "documentation": "http://doc.example.com",
                "description": "service description",
            }
        ]
    }
    version = {"version": "abc123"}


class TestOnlineNodeUpdateWithInvalidServices(InvalidResponseTests, NonInitialTests):
    """Test when updates have previously been run and the reported services are not valid"""

    services = {"services": [{"bad_key": "some_value"}]}


class TestOnlineNodeUpdateWithInvalidServiceTypes(InvalidResponseTests, NonInitialTests):
    """Test when updates have previously been run and the reported services types are not valid"""

    services = {
        "services": [
            {
                "url": "http://example.com",
                "name": "thredds",
                "type": ["some-bad-service-type"],
                "documentation": "http://doc.example.com",
                "description": "service description",
            }
        ]
    }
