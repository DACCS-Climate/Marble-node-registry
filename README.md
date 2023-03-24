# DACCS-node-registry

The purpose of this repository is to serve as a single source of truth for information on all DACCS nodes that constitute the DACCS network at any time. Active DACCS nodes will periodically retrieve this file and update their own local databases with the information contained within it.

## Usage

This repo is only meant to be updated by administrators who either (i) manage DACCS nodes or, (ii) want to deploy a new DACCS Node. 

If you want to deploy a new DACCS Node and connect it to the DACCS network (connecting a node to the DACCS network is what makes a node a DACCS node), then fork this repo and edit the node_registry.json file with information about the base URL at which your node can be accessed. Then, please submit a pull request with your changes. The DACCS Executive Committee will review the request to determine whether-or-not to allow your node to become a part of the network. Updating this repo is typically the last step in the journey for a node to federate with the network and ideally before getting to this point, you are already in conversations with the DACCS Executive Committee about your plans on being a part of the network.

If your are alsready part of the DACCS Network, then the only case where you might need to update this repo is if the base URL for your node changes. In which case, please submit the pull request with the new URL and the Executive Committee will approve it quickly.