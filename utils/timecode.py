def to_timecode(seconds: int | float) -> str:
    """
    Converts a duration in seconds into a formatted timecode.

    -> DD:HH:MM:SS or HH:MM:SS if shorter
    """

    # Ensure the input is an integer
    if not isinstance(seconds, int):
        seconds = int(seconds)

    # Calculate days, hours, minutes, and remaining seconds
    days = seconds // (3600 * 24)
    seconds -= days * (3600 * 24)

    hours = seconds // 3600
    seconds -= hours * 3600

    minutes = seconds // 60
    seconds -= minutes * 60

    # Format MM:SS as the base output
    res = "{:02}:{:02}".format(minutes, seconds)

    # Include hours if necessary
    if hours or days:
        res = "{:02}:".format(hours) + res

    # Include days if necessary
    if days:
        res = "{:02}:".format(days) + res

    return res
