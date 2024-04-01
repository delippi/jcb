# --------------------------------------------------------------------------------------------------


import copy
from datetime import datetime
import re

import jcb


# --------------------------------------------------------------------------------------------------

# Function mapping for variable strategy
function_map = {
    'min': min,
    'max': max,
}

# --------------------------------------------------------------------------------------------------

def datetime_from_conf(datetime_string):

    # Strip and non-numeric characters from the string
    datetime_string = re.sub(r'\D', '', datetime_string)

    # A string that is less 8 characters long is not valid
    jcb.abort_if(len(datetime_string) < 8,
                 f"The datetime \'{datetime_string}\' is not long enough to be a valid datetime.")

    # If length of string is less than 14 then pad with zeros
    if len(datetime_string) < 14:
        datetime_string += '0' * (14 - len(datetime_string))

    # Convert to datetime object
    return datetime.strptime(datetime_string, "%Y%m%d%H%M%S")


# --------------------------------------------------------------------------------------------------


def add_to_evolving_observing_system(evolving_observing_system, datetime, channel_values):

    # Temporary dictionary
    temp_dict = {}
    temp_dict['datetime'] = datetime
    temp_dict['channel_values'] = channel_values

    # Append to the evolving observing system
    evolving_observing_system.append(temp_dict)


# --------------------------------------------------------------------------------------------------


def process_satellite_chronicles(window_begin, window_final, chronicle):

    # Commissioned time for this platform
    # -----------------------------------
    commissioned = datetime_from_conf(chronicle['commissioned'])

    # Initial channel values
    # ----------------------
    channel_values = chronicle.get('channel_values')

    # Variables that are described in the chronicle
    # ---------------------------------------------
    channel_variables = chronicle.get('channel_variables').keys()
    num_variables = len(channel_variables)

    # Abort if the first variable is not simulated
    jcb.abort_if(channel_variables[0] != 'simulated',
                 "The first variable in the channel_variables must be \'simulated\'.")

   # Convert the list of channel_variables_strategies to actual function references
    channel_variables_func = [function_map[op] for op in chronicle['channel_variables'].values()]

    # For each channel (keys of channel_values) check values matches number of variables
    for channel, values in channel_values.items():
        jcb.abort_if(not len(values) == num_variables,
                     f"The number of values for each channel {channel} must match the number of "
                      "variables.")

    # Dictionary to hold the observing system as it evolves through the chronicles
    # ----------------------------------------------------------------------------
    evolving_observing_system = []

    # Store chronicle at the initial commissioned date
    add_to_evolving_observing_system(evolving_observing_system, commissioned, channel_values)

    # Get chronicles list
    # -------------------
    chronicles = chronicle.get('chronicles', [])

    # Validation checks on the chronicles
    # -----------------------------------

    # Check chronicles for chronological order and that they are unique
    action_dates = [datetime_from_conf(chronicle['action_date']) for chronicle in chronicles]
    jcb.abort_if(action_dates != sorted(action_dates),
                 "The chronicles are not in chronological order.")
    jcb.abort_if(len(action_dates) != len(set(action_dates)),
                 "The chronicles are not unique. Ensure no two chronicles have the same date.")

    # Loop through the chronicles and at each time there will be a complete set of channel_values
    # with the values specified by the chronicle.
    # -------------------------------------------------------------------------------------------
    for action_date, chronicle in zip(action_dates, chronicles):

        # If chronicle has channel_values key then simply update those channels
        if 'channel_values' in chronicle:

            # Check that the number of values provided for each channel matched the variables
            for channel, values in chronicle['channel_values'].items():
                jcb.abort_if(not len(values) == num_variables,
                             f"The number of values for each channel {channel} in chronicle with "
                             f"action date {chronicle['action_date']} does not have correct ."
                             "number of variables.")

            for channel, values in chronicle['channel_values'].items():
                channel_values[channel] = values

        # If chronicle has key adjust_variable_for_all_channels then update those variables for all
        # channels
        if 'adjust_variable_for_all_channels' in chronicle:
            variables = chronicle['adjust_variable_for_all_channels']['variables']
            values = chronicle['adjust_variable_for_all_channels']['values']
            for variable, value in zip(variables, values):
                for channel in channel_values.keys():
                    channel_values[channel][channel_variables.index(variable)] = value

        # If the chronicle has key revert_to_previous_chronicle
        if 'revert_to_previous_date_time' in chronicle:
            previous_datetime = datetime_from_conf(chronicle['revert_to_previous_date_time'])

            # Assert that previous datetime is equal to or after the commissioned date
            jcb.abort_if(previous_datetime < commissioned,
                         "The previous datetime is before the commissioned date.")

            # Find the nearest previous datetime in the action_dates list (without going over)
            index_of_previous = next((ind for ind, date in enumerate(action_dates) if date <
                                      previous_datetime), None)

            # Update the channel values to the previous chronicle (using the evolving observing system)
            channel_values = evolving_observing_system[index_of_previous]['channel_values']


        # Add the values after the action to the evolving observing system
        add_to_evolving_observing_system(evolving_observing_system, action_date, channel_values)


    # Now that the entire chronicle has been processed we can return the values to be used for
    # the window. If the window beginning and ending are both between the same action dates then the
    # values will be set to the earlier values. If the window straddles and action date then the
    # values have to be determined using the min/max strategy that the user wishes and has chosen
    # in the variables.

    # Sanity check on the expected input values
    # -----------------------------------------
    # Abort if the window begin/final are not a datetime objects
    jcb.abort_if(not isinstance(window_begin, datetime),
                 "The window begin must be a datetime object.")
    jcb.abort_if(not isinstance(window_final, datetime),
                 "The window final must be a datetime object.")

    # Abort if the window final is not after window begin
    jcb.abort_if(window_final <= window_begin,
                 "The window final must be after the window begin.")

    # Find the index of the nearest actions_date that is before or equal to window begin
    index_of_begin = next((ind for ind, date in enumerate(action_dates) if date <= window_begin),
                          None)

    # Find the index of the nearest actions_date that is before or equal to window end
    index_of_final = next((ind for ind, date in enumerate(action_dates) if date <= window_final),
                          None)

    # Extract actual values at times before window and begin and final
    channel_values_a = copy.deepcopy(evolving_observing_system[index_of_begin]['channel_values'])
    channel_values_b = copy.deepcopy(evolving_observing_system[index_of_final]['channel_values'])

    # Loop over channels
    for channel in channel_values_a.keys():

        # Index loop over variables
        for variable_index in range(num_variables):

            # Use strategy to determine value for the window
            channel_values_a[channel][variable_index] = \
                channel_variables_func[variable_index](channel_values_a[channel][variable_index],
                                                       channel_values_b[channel][variable_index])

    # Return the channel values
    return channel_values_a


# --------------------------------------------------------------------------------------------------
