# DACCS-node-registry

The purpose of this repository is to serve as a single source of truth for information on all DACCS nodes that 
constitute the DACCS network at any time. Active DACCS nodes will periodically retrieve this file and update their 
own local databases with the information contained within it.

## Access the registry

The registry can be accessed at the following URL:

https://raw.githubusercontent.com/DACCS-Climate/DACCS-node-registry/current-registry/node_registry.json

The registry is a JSON string that contains information about all nodes in the DACCS network. This file is regularly
updated so that the information provided is up-to-date.

## Add or update information about a DACCS node

This repo is only meant to be updated by administrators who either (i) manage DACCS nodes or, (ii) want to deploy a 
new DACCS Node. 

If you want to deploy a new DACCS Node and connect it to the DACCS network (connecting a node to the DACCS network 
is what makes a node a DACCS node), then fork this repo and edit the node_registry.json file with information about 
the base URL at which your node can be accessed. Then, please submit a pull request with your changes. The DACCS 
Executive Committee will review the request to determine whether-or-not to allow your node to become a part of the 
network. Updating this repo is typically the last step in the journey for a node to federate with the network and 
ideally before getting to this point, you are already in conversations with the DACCS Executive Committee about your 
plans on being a part of the network.

If you are already part of the DACCS Network and details about your node have changed (e.g. url, contact email, etc.). 
In which case, please submit the pull request with the new URL and the Executive Committee will approve it quickly.

When making changes to the node_registry.json file please only change or add the following values:
  - url (the publicly accessible URL of your node)
  - affiliation (the name of your organization, optional)
  - description (a short description of your node, optional)
  - icon_url (a publicly accessible url to an icon image for your node, optional)
  - location (latitude and longitude of your organization, optional)
  - contact (an email address that can be used by users to contact you if they have questions about your node)

## Testing

To run unittests contained in the tests/ directory:

```shell
pip install -r requirements.txt -r tests/requirements.txt
pytest ./tests
```
