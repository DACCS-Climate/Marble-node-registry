# DACCS-node-registry

The purpose of this repository is to serve as a single source of truth for information on all DACCS nodes that constitute the DACCS network at any time.

## Usage

This repo is only meant to be updated by administrators responsible for managing DACCS nodes. If you manage a node and want to connect it to the "network", then fork this repo and edit the node-registry.json file. Then, please submit a pull request for your changes. Active DACCS nodes will periodically retrieve this file and update their own local databases with the information contained within it.
