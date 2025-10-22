# Migrations are used to ensure that data provided by nodes that are using an
# older version of the schema are updated automatically to comply with the newest
# version of the schema.
#
# If a backwards incompatible change is introduced in the schema, please make a 
# new migration function here to ensure that older data is properly updated.
#
# Migration functions will be applied to each node's data in the order that they
# appear in the MIGRATIONS variable at the bottom of this file.
#
# All migration function should take a single argument which contains the node's
# data and modify that data in place.

def convert_keywords_to_types(data: dict) -> None:
    """
    Add service types if they don't exist.

    Since version 1.3.0 service "types" are now required. If they don't exist
    then they can be derived from service "keywords" which were used in place
    of "types" prior to this version.
    """

    keyword2type = {
        "catalog": "catalog",
        "data": "data",
        "jupyterhub": "jupyterhub",
        "other": "other",
        "service-wps": "wps",
        "service-wms": "wms",
        "service-wfs": "wfs",
        "service-wcs": "wcs",
        "service-ogcapi_processes": "ogcapi_processes"
    }
    for service in data["services"]:
        if "types" not in service:
            service["types"] = []
            for keyword in service["keywords"]:
                if (type_ := keyword2type.get(keyword)):
                    service["types"].append(type_)
            if not service["types"]:
                service["types"].append("other")


MIGRATIONS = (
    convert_keywords_to_types,
)
