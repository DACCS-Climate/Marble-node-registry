import json
import os
import sys
import jsonschema
import requests
import datetime
from copy import deepcopy

from migrations import MIGRATIONS

THIS_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.dirname(THIS_DIR)
SCHEMA_FILE = os.path.join(ROOT_DIR, "node_registry.schema.json")
CURRENT_REGISTRY = os.path.join(ROOT_DIR, "node_registry.json")


def _load_schema() -> dict:
    """
    Load the json schema from the 'node_registry.schema.json' file and return it
    as a dictionary.
    """
    with open(SCHEMA_FILE) as f:
        return json.load(f)


def _load_registry() -> dict:
    """
    Load the current node registry from the 'node_registry.json' file and return it
    as a dictionary.
    """
    with open(CURRENT_REGISTRY) as f:
        return json.load(f)


def _write_registry(registry: dict) -> None:
    """
    Write the registry as a json string to the 'node_registry.json' file.
    """
    with open(CURRENT_REGISTRY, "w") as f:
        json.dump(registry, f, indent=2)


def update_registry() -> None:
    """
    Update the 'node_registry.json' file with new data returned by each node.

    If the node is unresponsive, set the status field accordingly.
    """
    registry = _load_registry()
    schema = _load_schema()

    for name, data in registry.items():
        org_data = deepcopy(data)
        # set services and version
        services_url = None
        version_url = None
        for link in data["links"]:
            if link["rel"] == "collection":
                services_url = link["href"]
            elif link["rel"] == "version":
                version_url = link["href"]
        try:
            # This assumes the json is initially valid according to the schema
            services_response = requests.get(services_url, headers={"Accept": "application/json"})
            version_response = requests.get(version_url, headers={"Accept": "application/json"})
        except requests.exceptions.ConnectionError as e:
            # if either url fails, report that the node is offline
            data["status"] = "offline"
            sys.stderr.write(f"unable to access node named {name}. Error message: {e}\n")
            continue

        try:
            data["version"] = version_response.json().get("version", "unknown")
        except requests.exceptions.JSONDecodeError:
            registry[name] = org_data
            registry[name]["status"] = "unresponsive"
            sys.stderr.write(
                f"invalid json returned when accessing version for Node named {name}: {version_response.text}\n"
            )
            continue

        try:
            data["services"] = services_response.json().get("services", [])
        except requests.exceptions.JSONDecodeError:
            registry[name] = org_data
            registry[name]["status"] = "unresponsive"
            sys.stderr.write(
                f"invalid json returned when accessing services for Node named {name}: {services_response.text}\n"
            )
            continue

        try:
            for migration in MIGRATIONS:
                migration(data)
        except Exception as e:
            registry[name] = org_data
            registry[name]["status"] = "invalid_configuration"
            sys.stderr.write(f"unable to apply migrations for Node named {name}: {e}.")
            continue

        try:
            jsonschema.validate(instance=registry, schema=schema)
        except jsonschema.exceptions.ValidationError as e:
            registry[name] = org_data
            registry[name]["status"] = "invalid_configuration"
            sys.stderr.write(f"invalid configuration for Node named {name}: {e}\n")
        else:
            print(f"successfully updated Node named {name}")
            registry[name]["last_updated"] = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
            data["status"] = "online"

    _write_registry(registry)


if __name__ == "__main__":
    update_registry()
