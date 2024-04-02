# --------------------------------------------------------------------------------------------------


from datetime import datetime
import re

import jcb


# --------------------------------------------------------------------------------------------------


def datetime_from_conf(datetime_input):

    """
    Convert a datetime string in the format to a datetime object. The string can have any number of
    non-numeric characters in it. The function will strip all non-numeric characters and then pad
    with zeros if the string is less than 14 characters long. The string must be at least 8
    characters long to be a valid datetime string.

    Args:
        datetime_input (str or datetime object): The datetime string to convert.

    Returns:
        datetime: The datetime object.
    """

    # If the input is already a datetime object then return it
    if isinstance(datetime_input, datetime):
        return datetime_input

    # If not a string then abort
    jcb.abort_if(not isinstance(datetime_input, str),
                 f"The datetime \'{datetime_input}\' is not a string.")

    # A string that is less 8 characters long is not valid
    jcb.abort_if(len(datetime_input) < 8,
                 f"The datetime \'{datetime_input}\' must be at least 8 character (the length of "
                 "a date).")

    # Strip and non-numeric characters from the string and make at least 14 characters long
    datetime_string = re.sub('[^0-9]', '', datetime_input+'000000')[0:14]

    # Convert to datetime object
    return datetime.strptime(datetime_string, "%Y%m%d%H%M%S")


# --------------------------------------------------------------------------------------------------
