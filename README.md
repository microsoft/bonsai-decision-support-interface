#  bonsai decision support deployment
![msft Logo](./images/ms-logo.png)

This repository provides an example of a decision support deployment interface to a bonsai brain. The deployment interface connects to an exported brain and runs in a web browser.

- Supports *number* type states and action only (TODO: extend to other types)

## Pre-requisites

- Install python packages `pip install -r requirements.txt`
- An exported brain running (see [preview.bons.ai](preview.bons.ai)) and reachable via http requests at  `<exported-brain-url>`. For example below is the docker command for running an exported brain locally, reachable at `<exported-brain-url> = http://localhost:<port>`
    ```bash
    docker run -d -p <port>:5000 <acr_name>.azurecr.io/<workspace-id>/<brain-name>:1-linux-amd64
    ```

## Usage

1. Have an exported brain running and reachable at `<exported-brain-url>`.  
 **Note:** if no `<exported-brain-url>` is passed as an argument, the default exported-brain-url will be assume reachable at `'http://localhost:5000'`

    `streamlit run launch_decision_support.py <exported-brain-url>`

2. If you want to stop all running docker containers `docker stop $(docker ps -aq)`
