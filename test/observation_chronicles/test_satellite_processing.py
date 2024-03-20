# --------------------------------------------------------------------------------------------------


import copy
from datetime import datetime

import jcb
import pytest
import yaml


# --------------------------------------------------------------------------------------------------


# YAML File for testing

config_file = """
commissioned: '2009-04-14T00:00:00'
observer_type: satellite

simulated_channels: 1-3
active_channels: 1-3
channel_dependent_variables:
  err0:
    values: [0.5, 0.5, 0.5]
    value_across_window: max
  x1:
    values: [1.5, 1.5, 1.5]
    value_across_window: min

chronicles:

- action_date: "2009-05-01T00:00:00"
  justification: 'Remove from active channels'
  action:
    type: remove_active_channels
    channels: 1-2

- action_date: "2009-05-05T00:00:00"
  justification: 'Add to active channels'
  action:
    type: add_active_channels
    channels: 1

- action_date: "2009-05-10T00:00:00"
  justification: 'Remove simulated channels'
  action:
    type: remove_simulated_channels
    channels: 1

- action_date: "2009-05-15T00:00:00"
  justification: 'Add simulated channels'
  action:
    type: add_simulated_channels
    channels: 4
    channel_dependent_variables:
      err0: [1.01]
      x1: [2.01]

- action_date: "2009-05-15T00:00:00"
  justification: 'Activate channel 4'
  action:
    type: add_active_channels
    channels: 4

- action_date: "2009-05-25T00:00:00"
  justification: 'Change channel dependent variables for channels 3-4'
  action:
    type: adjust_channel_dependent_variables
    channels: 3-4
    channel_dependent_variables:
      err0: [0.6, 1.2]
"""

# Read the YAML file into a dictionary
satellite_chronicle = yaml.safe_load(config_file)


# --------------------------------------------------------------------------------------------------


def test_window_before_chronicles():

    window_begin = datetime.fromisoformat("2009-04-15T00:00:00")
    window_final = datetime.fromisoformat("2009-04-15T06:00:00")

    act, sim, vars = jcb.process_satellite_chronicles(window_begin, window_final,
                                                      satellite_chronicle)

    assert act == [1, 1, 1]
    assert sim == [1, 2, 3]
    assert vars['err0']['values'] == [0.5, 0.5, 0.5]
    assert vars['x1']['values'] == [1.5, 1.5, 1.5]


# --------------------------------------------------------------------------------------------------


def test_window_after_chronicles():

    window_begin = datetime.fromisoformat("2010-01-01T00:00:00")
    window_final = datetime.fromisoformat("2010-01-01T06:00:00")

    act, sim, vars = jcb.process_satellite_chronicles(window_begin, window_final,
                                                      satellite_chronicle)

    assert act == [-1, 1, 1]
    assert sim == [2, 3, 4]

    assert vars['err0']['values'] == [0.5, 0.6, 1.2]
    assert vars['x1']['values'] == [1.5, 1.5, 2.01]


# --------------------------------------------------------------------------------------------------


def test_window_straddles_chronicle():

    window_begin = datetime.fromisoformat("2009-04-30T00:00:00")
    window_final = datetime.fromisoformat("2009-05-02T00:00:00")

    act, sim, vars = jcb.process_satellite_chronicles(window_begin, window_final,
                                                      satellite_chronicle)

    assert act == [-1, -1, 1]
    assert sim == [1, 2, 3]
    assert vars['err0']['values'] == [0.5, 0.5, 0.5]
    assert vars['x1']['values'] == [1.5, 1.5, 1.5]


# --------------------------------------------------------------------------------------------------


def test_remove_simulated_channel():

    window_begin = datetime.fromisoformat("2009-05-09T00:00:00")
    window_final = datetime.fromisoformat("2009-05-11T00:00:00")

    act, sim, vars = jcb.process_satellite_chronicles(window_begin, window_final,
                                                      satellite_chronicle)

    assert act == [-1, 1]
    assert sim == [2, 3]
    assert vars['err0']['values'] == [0.5, 0.5]
    assert vars['x1']['values'] == [1.5, 1.5]


# --------------------------------------------------------------------------------------------------


def test_add_simulated_channel_and_activate():

    window_begin = datetime.fromisoformat("2009-05-14T21:00:00")
    window_final = datetime.fromisoformat("2009-05-15T06:00:00")

    act, sim, vars = jcb.process_satellite_chronicles(window_begin, window_final,
                                                      satellite_chronicle)

    assert act == [-1, 1, 1]
    assert sim == [2, 3, 4]
    assert vars['err0']['values'] == [0.5, 0.5, 1.01]
    assert vars['x1']['values'] == [1.5, 1.5, 2.01]


# --------------------------------------------------------------------------------------------------


def test_no_chronicles():

    # Copy the chronicle and remove the chronicles
    no_chronicles = copy.deepcopy(satellite_chronicle)
    del no_chronicles['chronicles']

    window_begin = datetime.fromisoformat("2009-04-30T00:00:00")
    window_final = datetime.fromisoformat("2009-05-02T00:00:00")

    act, sim, vars = jcb.process_satellite_chronicles(window_begin, window_final, no_chronicles)

    assert act == [1, 1, 1]
    assert sim == [1, 2, 3]
    assert vars['err0']['values'] == [0.5, 0.5, 0.5]
    assert vars['x1']['values'] == [1.5, 1.5, 1.5]


# --------------------------------------------------------------------------------------------------


def test_no_channel_dep_variables():

    # Copy the chronicle and remove the chronicles
    no_variables = copy.deepcopy(satellite_chronicle)
    del no_variables['channel_dependent_variables']

    # Remove if the action type is adjust_channel_dependent_variables
    action_type = 'adjust_channel_dependent_variables'
    no_variables['chronicles'] = [chronicle for chronicle in no_variables['chronicles'] if
                                  chronicle['action']['type'] != action_type]

    # Loop over actions and remove channel_dependent_variables
    for chronicle in no_variables['chronicles']:
        if 'channel_dependent_variables' in chronicle['action']:
            del chronicle['action']['channel_dependent_variables']

    window_begin = datetime.fromisoformat("2009-04-30T00:00:00")
    window_final = datetime.fromisoformat("2009-05-02T00:00:00")

    act, sim, _ = jcb.process_satellite_chronicles(window_begin, window_final, no_variables)

    assert act == [-1, -1, 1]
    assert sim == [1, 2, 3]


# --------------------------------------------------------------------------------------------------


# Main entry point
if __name__ == "__main__":
    pytest.main()


# --------------------------------------------------------------------------------------------------
