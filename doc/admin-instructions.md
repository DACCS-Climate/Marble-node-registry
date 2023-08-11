# Admin instructions

## Allow the registry update script to push to a protected branch

The [registry-update](../.github/workflows/registry-update.yml) workflow runs the 
[update.py](../marble_node_registry/update.py) script and pushes the changes to the `current-registry` branch. 

The `current-registry` branch is locked (and *should remain locked*) so in order to allow the workflow to push 
changes to this branch we need to provide the workflow with a personal access token (PAT) of an admin or maintainer
user. 

The following steps must be taken by a user with "Admin" or "Maintainer" level permissions for this repository.

1. create a PAT on GitHub with permission to write to this repository.
    - On github.com go to user settings: Settings > Developer Settings > Personal access tokens
    - Follow the steps to create a PAT (remember the value of the token for the next step)
2. add that PAT to workflows for this repo
    - Now go to the settings for this repo: Settings > Secrets and variables > Actions
    - Create a new repository secret name `DACCS_NODE_REGISTRY_PAT` with the value of the token from step 1

Remember that if you set an expiry date for this token you'll need to repeat these steps when the token expires.
