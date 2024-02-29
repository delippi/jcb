# --------------------------------------------------------------------------------------------------

def abort_if(condition: bool, message: str):

    """
    Raises a ValueError if the condition is True.
    """

    if condition:
        print("\033[31m" + message + "\033[0m")
        raise ValueError(message)

# --------------------------------------------------------------------------------------------------
