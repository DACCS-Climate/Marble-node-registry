## Registry update

I would like to (choose one):

- [ ] add a new Node to the DACCS network
- [ ] update an existing Node in the DACCS network

## Guidelines

- only submit changes to the `node_registry.json` file
- only make changes to a single Node listed in the registry in the pull request
- only make changes to the following keys (all others are updated automatically):
  - `date_added`
  - `affiliation`
  - `description`
  - `location`
  - `contact`
  - `links`
- you may also change the name of the node (the key at the root of the json string) but ensure that the name is not already in use
- see `README.md` for a description of the values and see `doc/node_registry.example.json` for examples.

## Next Steps

Submitting this pull request is typically the last step in the journey for a node to federate with the network and 
ideally before getting to this point, you are already in conversations with the DACCS Executive Committee about your 
plans on being a part of the network.

If you have not already done so please reach out to the DACCS Executive Committee. This pull request will not be merged
in until then.
