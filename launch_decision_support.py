#!/usr/bin/env python3
"""
MSFT Bonsai, decision support deployment template
Copyright 2020 Microsoft
Usage:
  streamlit run launch_decision_support.py
"""

from typing import Dict, List, Union
import streamlit as st
import base64, requests, argparse
import pandas as pd
import SessionState  # from https://gist.github.com/tvst/036da038ab3e999a64497f42de966a92
from exported_brain_interface import ExportedBrainPredictor


def _findkeys(node: Union[Dict, List], kv: str):
    if isinstance(node, list):
        for i in node:
            for x in _findkeys(i, kv):
                yield x
    elif isinstance(node, dict):
        if kv in node:
            yield node[kv]
        for j in node.values():
            for x in _findkeys(j, kv):
                yield x


def get_state_action_list(get_request: List):

    req_items = list(_findkeys(get_request, "required"))
    states = req_items[1]
    actions = req_items[2]

    return states, actions


def initialize_brain_interface(exported_brain_url="http://localhost:5000",):
    """Initializes an interface to an exported brain
    in: url corresponding to running exported brain docker container
    out: brain_interface, list of states names, list of action names
    """
    brain = ExportedBrainPredictor(predictor_url=exported_brain_url)
    r = requests.get(exported_brain_url + "/v1/api.json").json()
    state_list, action_list = get_state_action_list(
        r["paths"]["/v1/prediction"]["post"]
    )
    return brain, state_list, action_list


def get_table_download_link(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(
        csv.encode()
    ).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}" download="bonsai_state_action.csv">Download .csv file</a>'
    return href


def main():
    # Initialize exported brain interface
    brain, state_list, action_list = initialize_brain_interface(
        exported_brain_url=args.exported_brain_url
    )

    # Define state and action schema
    state = {i: [] for i in state_list}
    action = {i: [] for i in action_list}
    state_action_log = dict(state, **action)

    # Initializing iteration count, state_action_log_df. Then session_state.iteration_count will persist on a per user basis
    session_state = SessionState.get(
        iteration_count=0, state_action_log_df=pd.DataFrame(state_action_log)
    )

    st.set_page_config(
        page_title="Bonsai deployment",
        page_icon="./images/msft_icon.png",
        layout="centered",
        initial_sidebar_state="auto",
    )

    # ---------
    # Sidebar
    # ---------
    st.sidebar.markdown("Brain running at {}".format(args.exported_brain_url))
    st.sidebar.markdown("### Usage")
    st.sidebar.markdown(
        "- Enter value of each state below then click `Get Brain action` to obtain Brain's actions"
    )
    st.sidebar.markdown("- To reset chart click `Reset`")
    st.sidebar.markdown(" ")
    st.sidebar.markdown("### Brain states")
    for key in state.keys():
        state[key] = st.sidebar.number_input("{} ".format(key))

    st.sidebar.markdown("## Reset")
    reset_button = st.sidebar.button("Reset",)

    st.sidebar.markdown("## Iteration count")
    if reset_button:
        session_state.iteration_count = 0
        session_state.state_action_log_df = pd.DataFrame(state_action_log)
        add_text = st.sidebar.write(
            "Iteration count: {}".format(session_state.iteration_count)
        )
    else:
        add_text = st.sidebar.write(
            "Iteration count: {}".format(session_state.iteration_count)
        )

    # -----------
    # Main page
    # -----------

    st.image("./images/bonsai-logomark.png", width=70)
    """
    # Bonsai decision support  
    A template to run a decision support interface with a locally running exported Brain.  
    More info on [preview.bons.ai](https://preview.bons.ai)
    """
    get_brain_action = st.button(label="Get Brain action")

    "#### Brain Actions  "
    "  "
    if get_brain_action:
        with st.spinner("Wait for it..."):
            session_state.iteration_count = session_state.iteration_count + 1
            action = brain.get_action(state)
            session_state.state_action_log_df = session_state.state_action_log_df.append(
                dict(state, **action), ignore_index=True
            )

    for key in action.keys():
        st.markdown("{}: {}".format(key, action[key]))

    "#### State and action table"

    st.table(session_state.state_action_log_df)
    st.markdown(
        get_table_download_link(session_state.state_action_log_df),
        unsafe_allow_html=True,
    )

    "#### State and action chart vs iteration count "
    "  "
    st.line_chart(session_state.state_action_log_df)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="launch a decision support interface to an exported brain"
    )
    parser.add_argument(
        "exported_brain_url",
        type=str,
        nargs="?",
        default="http://localhost:5000",
        help="brain url of a running exported brain",
    )
    args = parser.parse_args()
    print("Connecting to exported brain running at: {}".format(args.exported_brain_url))
    main()
