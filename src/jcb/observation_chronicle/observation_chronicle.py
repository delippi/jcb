# --------------------------------------------------------------------------------------------------

from datetime import datetime
import isodate
import jcb
import os
import yaml

# --------------------------------------------------------------------------------------------------

class ObservationChronicle():

    # ----------------------------------------------------------------------------------------------

    def __init__(self, chronicle_path, window_begin, window_length):

        # Keep the chronicle path
        self.chronicle_path = chronicle_path

        # Convert the window_begin coming in as a string to a datetime object
        self.window_begin = datetime.strptime(window_begin, '%Y-%m-%dT%H:%M:%SZ')

        # Add window_length to window_begin
        self.window_final = self.window_begin + isodate.parse_duration(window_length)

        # Save the most recent observer that was passed to the class. This can be used to avoid
        # re-precessing the chronicles if the same observer is used multiple times.
        self.last_observer = ''

        # Read all the chronicles into a dictionary where the key is the observation type and the
        # value is the chronicle dictionary

        # List all the yaml files in the observation chronicle path
        chronicle_files = [f for f in os.listdir(chronicle_path)
                           if f.endswith('.yaml')]

        # Create dictionary of chronicles
        self.chronicles = {}

        # Read each chronicle file
        for chronicle_file in chronicle_files:

            # Read the YAML file
            with open(os.path.join(chronicle_path, chronicle_file), 'r') as file:
                self.chronicles[chronicle_file[:-5]] = yaml.safe_load(file)

    # ----------------------------------------------------------------------------------------------

    def use_observer(self, observer):

        # If there is no chronicle for this type then return True
        if observer not in self.chronicles:
            return True

        # Get the chronicle for the observation type
        obs_chronicle = self.chronicles[observer]

        # Commissioned date
        commissioned_str = obs_chronicle.get('commissioned')
        commissioned = datetime.fromisoformat(commissioned_str)

        # Decommissioned date (if present)
        decommissioned_str = obs_chronicle.get('decommissioned', None)
        if decommissioned_str:
            decommissioned = datetime.fromisoformat(decommissioned_str)

        # First check that the commissioned period overlaps the window
        # ------------------------------------------------------------

        # If the widow final is before the commissioned date then return False
        if self.window_final <= commissioned:
            return False

        # If the instrument is decommissioned and the window begin is after the decommissioned
        # date then return False
        if decommissioned_str and self.window_begin >= decommissioned:
            return False

        # If made it through all the checks then the data is active and should be used
        # ----------------------------------------------------------------------------
        return True

    # ----------------------------------------------------------------------------------------------

    def __process_satellite_chronicles__(self, caller, observer):

        # Only re-process the chronicle if the observer has changed
        if self.last_observer != observer:

            # Check that there is a chronicle for this type
            jcb.abort_if(observer not in self.chronicles,
                         f"No chronicle found for observation type {observer}. However templates " +
                         f"in the observation file require a chronicle as it is required by the " +
                         f"function {caller} that is invoked in the templates.")

            # Get the chronicle for the observation type
            obs_chronicle = self.chronicles[observer]

            # Abort if the window begin is after the decommissioned date
            decommissioned_str = obs_chronicle.get('decommissioned', None)
            if decommissioned_str:
                decommissioned = datetime.fromisoformat(decommissioned_str)
                jcb.abort_if(self.window_begin >= decommissioned,
                             f"The window begin is after the decommissioned date for " +
                             f"observation type {observer}.")

            # Abort if the type is not satellite
            jcb.abort_if(obs_chronicle['observer_type'] != 'satellite',
                         f"The template function {caller} was called for observation type " +
                         f"{observer} but the chronicle for this observation type is not " +
                         f"satellite, found {obs_chronicle['observer_type']}. ")

            # Process the satellite chronicle for this observer
            self.active_channels, self.simulated_channels, self.observation_errors = \
            jcb.process_satellite_chronicles(self.window_begin, self.window_final, obs_chronicle)

            # Update the last observer
            self.last_observer = observer

        # Return the requested data
        if caller == 'get_satellite_simulated_channels':
            return self.simulated_channels
        if caller == 'get_satellite_active_channels':
            return self.active_channels
        if caller == 'get_satellite_observation_errors':
            return self.observation_errors

    # ----------------------------------------------------------------------------------------------


    def get_satellite_simulated_channels(self, observer):

        return self.__process_satellite_chronicles__('get_satellite_simulated_channels', observer)


    # ----------------------------------------------------------------------------------------------

    def get_satellite_active_channels(self, observer):

        return self.__process_satellite_chronicles__('get_satellite_active_channels', observer)


    # ----------------------------------------------------------------------------------------------

    def get_satellite_observation_errors(self, observer):

        return self.__process_satellite_chronicles__('get_satellite_observation_errors', observer)


# --------------------------------------------------------------------------------------------------
