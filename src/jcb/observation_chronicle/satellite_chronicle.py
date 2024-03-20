# --------------------------------------------------------------------------------------------------

import copy
from datetime import datetime
import jcb

# --------------------------------------------------------------------------------------------------

def __remove_active_channels__(action, active_channels):

    """
    Remove active channels from the active channels list.

    This action is non intrusive in the sense that other quantities do not need to be adjusted at
    the same time. It only removes channels from the active list. The only condition/check is that
    the channels to remove must already be active

    Args:
        action (dict): The action dictionary from the observation chronicle.
        active_channels (set): The set of active channels.

    Returns:
        active_channels (set): The updated set of active channels.
    """

    # Get the active channels to remove from the action dictionary
    active_channels_to_remove = jcb.parse_channels_set(action['channels'])

    # Abort if any of the channels to remove are not already active
    jcb.abort_if(not active_channels_to_remove.issubset(active_channels),
                 "Trying to remove an active channel that is not currently active.")

    # Remove the active channels
    return active_channels - jcb.parse_channels_set(action['channels'])

# --------------------------------------------------------------------------------------------------

def __add_active_channels__(action, active_channels, simulated_channels):

    """
    Add active channels to the active channels list.

    This action requires that the active channels being added are already simulated. It only adds
    channels to the active list. It does not impact the simulated channels or the chanel dependent
    variables.

    Args:
        action (dict): The action dictionary from the observation chronicle.
        active_channels (set): The set of active channels.
        simulated_channels (set): The set of simulated channels.

    Returns:
        active_channels (set): The updated set of active channels.
    """

    # Get the active channels to add from the action dictionary
    active_channels_to_add = jcb.parse_channels_set(action['channels'])

    # Abort if any of the channels to add are not simulated
    jcb.abort_if(not active_channels_to_add.issubset(simulated_channels),
                 "You cannot add an active channel that is not simulated.")

    # Add the active channels
    return active_channels | active_channels_to_add

# --------------------------------------------------------------------------------------------------

def __add_simulated_channels__(action, simulated_channels, channel_dep_variables):

    """
    Add simulated channels to the simulated channels list.

    If channel dependent variables are not handled by the chronicles then this action is non
    intrusive in the sense that other quantities do not need to be adjusted at the same time.
    If channel dependent variables are handled by the chronicles then new values must be provided
    for each variable.

    Args:
        action (dict): The action dictionary from the observation chronicle.
        simulated_channels (set): The set of simulated channels.
        channel_dep_variables (dict): Dictionary of lists of channel dependent variables.

    Returns:
        simulated_channels (set): The updated set of simulated channels.
        channel_dep_variables (dict): The updated dictionary of channel dependent variables.
    """

    # Get the simulated channels to add from the action dictionary
    simulated_channels_to_add = jcb.parse_channels_set(action['channels'])

    # Add the simulated channels
    simulated_channels = simulated_channels | simulated_channels_to_add

    # If the channel dependant variables are being handled by the chronicles then new values must
    # be provided foreach new channel
    if channel_dep_variables:

        # Convert to lists
        simulated_channels_l = list(simulated_channels)
        simulated_channels_to_add_l = list(simulated_channels_to_add)

        # Get the new channel dependent variables
        new_cdv = action.get('channel_dependent_variables')

        # Abort if the new variables are of the same length as number of simulated channels to add
        for key, value in new_cdv.items():

            jcb.abort_if(not len(value) == len(simulated_channels_to_add),
                         f"The number of values provided for {key} does not match the number of " +
                         f"simulated channels to add.")

            # Reference to the variable in the main dictionary
            cdv_values = channel_dep_variables[key]['values']

            # Insert the new values at the appropriate position
            for ind, channel in enumerate(simulated_channels_l):

                # If the channel is in the new channels then add the new variable at the correct
                # position
                if channel in simulated_channels_to_add_l:
                    cdv_values.insert(ind, value[simulated_channels_to_add_l.index(channel)])

    return simulated_channels, channel_dep_variables

# --------------------------------------------------------------------------------------------------

def __remove_simulated_channels__(action, simulated_channels, channel_dep_variables):

    """
    Remove simulated channels from the simulated channels list.

    If channel dependent variables are not handled by the chronicles then this action is non
    intrusive in the sense that other quantities do not need to be adjusted at the same time.
    If channel dependent variables are handled by the chronicles then they must be removed as well.

    Args:
        action (dict): The action dictionary from the observation chronicle.
        simulated_channels (set): The set of simulated channels.
        channel_dep_variables (dict): Dictionary of lists of channel dependent variables.

    Returns:
        simulated_channels (set): The updated set of simulated channels.
        channel_dep_variables (dict): The updated dictionary of channel dependent variables.
    """

    # Save incoming simulated channels as list
    simulated_channels_l = list(simulated_channels)

    # Get the simulated channels to remove from the action dictionary
    simulated_channels_to_remove = jcb.parse_channels_set(action['channels'])

    # Abort if any of the channels to remove are not already simulated
    jcb.abort_if(not simulated_channels_to_remove.issubset(simulated_channels),
                 "Trying to remove a simulated channel that is not currently simulated.")

    # Remove the simulated channels
    simulated_channels = simulated_channels - simulated_channels_to_remove

    # If the channel dependant variables are being handled by the chronicles then they must be
    # removed as well
    if channel_dep_variables:

        # Convert to lists
        simulated_channels_to_remove_l = list(simulated_channels_to_remove)

        # Gather the indices of the simulated_channels_l that were removed
        indices_to_remove = [simulated_channels_l.index(channel) for channel in
                             simulated_channels_to_remove_l]

        # Abort if the new variables are of the same length as the new simulated channels
        jcb.abort_if(not len(simulated_channels_to_remove_l) == len(indices_to_remove),
                     "There is a discrepancy in the number of simulated channels and the number " +
                     "of values for the channel dependent variables.")

        # Loop over the channel dependent variables and remove the values at the appropriate
        # position
        for value in channel_dep_variables.values():
            for ind in sorted(indices_to_remove, reverse=True):
                del value['values'][ind]

    return simulated_channels, channel_dep_variables

# --------------------------------------------------------------------------------------------------

def __adjust_channel_dependent_variables__(action, channel_dep_variables, simulated_channels):

    """
    Adjust the channel dependent variables.

    This action is non intrusive in the sense that other quantities do not need to be adjusted at
    the same time. It only adjusts the channel dependent variables.

    Args:
        action (dict): The action dictionary from the observation chronicle.
        channel_dep_variables (dict): Dictionary of lists of channel dependent variables.

    Returns:
        channel_dep_variables (dict): The updated dictionary of channel dependent variables.
    """

    jcb.abort_if(channel_dep_variables is None,
                    "An action to adjust channel dependent variables was found but no initial " +
                    "channel dependent variables were present in the observation chronicle.")

    # Get the channels and adjusted variables from the action dictionary
    channels = jcb.parse_channels_set(action['channels'])
    adjusted_variables = action['channel_dependent_variables']

    # Create list of channel dependent variables
    cdv_base = set(channel_dep_variables.keys())
    cdv_adjusted = set(adjusted_variables.keys())

    # Abort if the adjusted is not a subset of the base
    jcb.abort_if(not cdv_adjusted.issubset(cdv_base),
                 f"The adjusted channel dependent variables {cdv_adjusted} are not a subset " +
                 f"of the base channel dependent variables {cdv_base}.")

    # Abort if any channels are not simulated
    jcb.abort_if(not channels.issubset(simulated_channels),
                 "The channels to adjust are not simulated.")

    # Loop over the variables to be adjusted
    for key, value in adjusted_variables.items():

        # Check that the number of adjusted variables matches the number of channels
        jcb.abort_if(not len(value) == len(channels),
                     f"The number of adjusted variables does not match the number of channels " +
                     f"for variable {key}.")

        for ind, channel in enumerate(channels):
            channel_dep_variables[key]['values'][list(simulated_channels).index(channel)] = \
                                                                                          value[ind]

    return channel_dep_variables

# --------------------------------------------------------------------------------------------------

def apply_action(action, active_channels, simulated_channels, channel_dep_variables):

    """
    Apply the action to the active channels, simulated channels, and channel dependent variables.

    Args:
        action (dict): The action dictionary from the observation chronicle.
        active_channels (set): The set of active channels.
        simulated_channels (set): The set of simulated channels.
        channel_dep_variables (dict): Dictionary of list of channel dependent variables.

    Returns:
        active_channels (set): The updated set of active channels.
        simulated_channels (set): The updated set of simulated channels.
        channel_dep_variables (dict): The updated dictionary of list of channel dependent
        variables.
    """

    # Remove active channels
    if action['type'] == 'remove_active_channels':
        active_channels = __remove_active_channels__(action, active_channels)

    # Add active channels
    if action['type'] == 'add_active_channels':
        active_channels = __add_active_channels__(action, active_channels, simulated_channels)

    # Remove simulated channels
    if action['type'] == 'remove_simulated_channels':
        simulated_channels, channel_dep_variables = __remove_simulated_channels__(action,
                                                                                 simulated_channels,
                                                                              channel_dep_variables)

    # Add simulated channels
    if action['type'] == 'add_simulated_channels':
        simulated_channels, channel_dep_variables = __add_simulated_channels__(action,
                                                                               simulated_channels,
                                                                              channel_dep_variables)

    # Adjust the channel dependent variables
    if action['type'] == 'adjust_channel_dependent_variables':
        channel_dep_variables = __adjust_channel_dependent_variables__(action,
                                                                       channel_dep_variables,
                                                                       simulated_channels)

    # Return everything
    return active_channels, simulated_channels, channel_dep_variables

# --------------------------------------------------------------------------------------------------

def process_satellite_chronicles(window_begin, window_final, obs_chronicle):

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

    # Extract initial values
    # ----------------------
    # Parse initial channel lists (for simplicity these are sets)
    active_channels = jcb.parse_channels_set(obs_chronicle['active_channels'])
    simulated_channels = jcb.parse_channels_set(obs_chronicle['simulated_channels'])

    # Optionally the chronicle may describe come channel dependent variables (dict of lists)
    channel_dependent_variables = copy.deepcopy(obs_chronicle.get('channel_dependent_variables',
                                                                  None))

    # Check on elements of initial lists
    # ----------------------------------
    # The elements of the active channels must be a subset of the simulated channels
    jcb.abort_if(not active_channels.issubset(simulated_channels),
                 "The active channels must be a subset of the simulated channels.")

    # If channel dependent variables are provided they should match the length of simulated channels
    if channel_dependent_variables is not None:
        for key, value in channel_dependent_variables.items():
            jcb.abort_if(not len(value['values']) == len(simulated_channels),
                         f"The length of the channel_dependent_variables {key} must match the " +
                         f"length of the simulated channels.")

    # Get chronicles list
    # -------------------
    chronicles = obs_chronicle.get('chronicles', [])

    # Set flags to record when status at window extremes is set
    window_begin_assigned = False
    window_final_assigned = False

    # Loop over chronicles up to (and including) the beginning of the window
    for ind, chronicle in enumerate(chronicles):

        # Save the date of the current chronicle
        action_date = chronicle.get('action_date')
        # If action date from the conf is a string convert to datetime
        if isinstance(action_date, str):
            action_date = datetime.fromisoformat(action_date)

        # Ensure the correct ordering of chronicles
        # -----------------------------------------
        if ind == 0:
            # If first chronicle save the action time
            previous_action_time = action_date
        else:
            # For later chronicles check the order
            jcb.abort_if(previous_action_time > action_date,
                         "The chronicles are not in chronological order.")

        # If the action_date is after the window beginning then save the current state
        if action_date > window_begin:
            active_channels_begin = active_channels
            simulated_channels_begin = simulated_channels
            if channel_dependent_variables:
                channel_dependent_variables_begin = copy.deepcopy(channel_dependent_variables)
            window_begin_assigned = True

        # If action date is after the window final then save and break
        if action_date > window_final:
            active_channels_final = active_channels
            simulated_channels_final = simulated_channels
            if channel_dependent_variables:
                channel_dependent_variables_final = copy.deepcopy(channel_dependent_variables)
            window_final_assigned = True
            # Any chronicles after the window are not relevant
            break

        # Apply the action to the active channels, simulated channels and channel dependent vars
        active_channels, simulated_channels, channel_dependent_variables = apply_action(chronicle['action'],
                                                                               active_channels,
                                                                               simulated_channels,
                                                                               channel_dependent_variables)

    # Set window extremes if they did not intersect with the chronicles
    if not window_begin_assigned:
        active_channels_begin = active_channels
        simulated_channels_begin = simulated_channels
        if channel_dependent_variables:
            channel_dependent_variables_begin = copy.deepcopy(channel_dependent_variables)
    if not window_final_assigned:
        active_channels_final = active_channels
        simulated_channels_final = simulated_channels
        if channel_dependent_variables:
            channel_dependent_variables_final = copy.deepcopy(channel_dependent_variables)

    # Only simulate / assimilate channels that are active at both the beginning and end of the
    # window. Convert back to lists.
    active_channels = list(active_channels_begin & active_channels_final)
    simulated_channels = list(simulated_channels_begin & simulated_channels_final)

    # Active channels is an array of -1 and 1. -1 if the channel is in the simulated list but
    # not the active list. 1 otherwise
    active_channels = [1 if channel in active_channels else -1 for channel in
                        simulated_channels]

    # For each channel dependent variable pick the maximum value
    if channel_dependent_variables:
        for variable_name, variable_dict in channel_dependent_variables.items():

            # Can take the maximum or minimum value across the window
            method = variable_dict.get('value_across_window', 'max').lower()

            # Values and begin and final
            values_begin = channel_dependent_variables_begin[variable_name]['values']
            values_final = channel_dependent_variables_final[variable_name]['values']

            if method == 'max':
                value['values'] = [max(values_begin[ind], values_final[ind])
                                   for ind in range(len(value['values']))]
            elif method == 'min':
                value['values'] = [min(values_begin[ind], values_final[ind])
                                   for ind in range(len(value['values']))]
            else:
                jcb.abort("The value_across_window must be max or min.")

    return active_channels, simulated_channels, channel_dependent_variables

# --------------------------------------------------------------------------------------------------
