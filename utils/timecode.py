def to_timecode(seconds: int | float):
    if not isinstance(seconds, int):
        seconds = int(seconds)

    days = seconds // (3600 * 24)
    seconds -= days * (3600 * 24)

    hours = seconds // 3600
    seconds -= hours * 3600

    minutes = seconds // 60
    seconds -= minutes * 60

    res = "{:02}:{:02}".format(minutes, seconds)

    if hours or days:
        res = "{:02}:".format(hours) + res

    if days:
        res = "{:02}:".format(days) + res

    return res
