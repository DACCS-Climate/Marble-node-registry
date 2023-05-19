import json
import os
import sys
import jsonschema
import requests
import datetime

THIS_DIR = os.path.join(os.path.dirname(__file__))
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
        json.dump(registry, f)


def _validate_registry_update(registry, node_name, key, value, schema):
    """
    Set registry[node_name][key] to value iff doing so results in a registry
    that is valid according to schema; and return True. Otherwise, do nothing and
    return False.
    """
    old_value = registry[node_name].get(key)
    registry[node_name][key] = value
    try:
        jsonschema.validate(instance=registry, schema=schema)
    except jsonschema.exceptions.ValidationError:
        if old_value is None:
            registry[node_name].pop(key)
        else:
            registry[node_name][key] = old_value
        return False
    registry[node_name]["last_updated"] = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
    return True


def update_registry() -> None:
    """
    Update the 'node_registry.json' file with new data returned by each node.

    If the node is unresponsive, set the status field accordingly.
    """
    registry = _load_registry()
    schema = _load_schema()

    for name, data in registry.items():
        # set services and version
        try:
            services_response = requests.get(os.path.join(data["url"], "services"))
            version_response = requests.get(os.path.join(data["url"], "version"))
        except requests.exceptions.ConnectionError as e:
            # if either url fails, report that the node is offline
            data["status"] = "offline"
            sys.stderr.write(f"unable to access node named {name} at url {data['url']}. Error message: {e}\n")
            continue

        version = version_response.text
        if not _validate_registry_update(registry, name, "version", version, schema):
            data["status"] = "invalid_configuration"
            sys.stderr.write(f"invalid configuration caused by version for Node named {name}: {version}\n")
            continue

        try:
            services = services_response.json()
        except requests.exceptions.JSONDecodeError:
            data["status"] = "unresponsive"
            sys.stderr.write(
                f"invalid json returned when accessing services for Node named {name}: {services_response.text}\n"
            )
            continue

        if not _validate_registry_update(registry, name, "services", services["services"], schema):
            data["status"] = "invalid_configuration"
            sys.stderr.write(
                f"invalid configuration caused by services for Node named {name}: {services['services']}\n"
            )
            continue

        print(f"successfully updated Node named {name} at url {data['url']}")
        data["status"] = "online"

    _write_registry(registry)


if __name__ == "__main__":
    update_registry()
