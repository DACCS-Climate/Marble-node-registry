# DACCS-node-registry

The purpose of this repository is to serve as a single source of truth for information on all DACCS nodes that 
constitute the DACCS network at any time. Active DACCS nodes will periodically retrieve this file and update their 
own local databases with the information contained within it.

## Usage

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
  - `date_added` (the date the node was originally added to the network, this should only be updated once)
  - `affiliation` (the name of your organization, optional)
  - `description` (a short description of your node, optional)
  - `location` (latitude and longitude of your organization, optional)
  - `contact` (an email address that can be used by users to contact you if they have questions about your node)
  - `links -> version` (see links table below)
  - `links -> collection` (see links table below)
  - `links -> service` (see links table below)

The `links` key should contain links that describe and provide access to your node. Please see the table below
for a description of some link values that may be useful. Only `version`, `collection`, and `home` are required.

| `rel`                                              | Meaning                                                                                                                                                         | 
|----------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `about`                                            | URL to a summary or purpose of the node                                                                                                                         |
| `author`                                           | URL to the maintainer/institution of the node                                                                                                                   |
| `acl`                                              | Endpoint to Access Control List such as the `/magpie` endpoint or another access management method                                                              |
| `collection`                                       | URL to the `/services` endpoint of the node (required)                                                                                                          |
| `cite-as` <br> `publication`                       | Attribution by researchers to reference the node when using it for publications                                                                                 |
| `copyright` <br> `license` <br> `terms-of-service` | Legal use of the node                                                                                                                                           |
| `describedby`                                      | URL to full documentation and details of the node, its purpose and so on                                                                                        | 
| `edit`                                             | A self-reference to https://github.com/DACCS-Climate/DACCS-node-registry or anywhere that the specific node registry entry to redirect users where to update it | 
| `service`                                          | URL to the landing page of the node (required)                                                                                                                  |
| `service-desc`                                     | URL to the `/components` endpoint of the node (if available)                                                                                                    |
| `icon`                                             | Logo of the institution of specific node                                                                                                                        | 
| `status`                                           | URL to a monitoring service endpoint, such as `/canarie` or another alternative                                                                                 | 
| `version`                                          | URL to the `/version` endpoint of the node (required)                                                                                                           |
| `version-history`                                  | link to https://github.com/bird-house/birdhouse-deploy/blob/master/CHANGES.md or similar                                                                        |

## Testing

To run unittests contained in the tests/ directory:

```shell
pip install -r requirements.txt -r tests/requirements.txt
pytest ./tests
```
