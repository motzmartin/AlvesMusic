import time

def duration_str(duration: int):
    if duration < 3600:
        return time.strftime("%M:%S", time.gmtime(duration))

    elif duration < 3600 * 24:
        return time.strftime("%H:%M:%S", time.gmtime(duration))

    return time.strftime("%d:%H:%M:%S", time.gmtime(duration))
