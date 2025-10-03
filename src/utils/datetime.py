from datetime import datetime, timedelta


# Increments a timestamp by the smallest possible unit (1 microsecond), in terms of DB precision.
# This is used to avoid returning the same record again when querying for updates.
# FIXME: Hardcoded
def increment_datetime(timestamp: datetime) -> datetime:
    return timestamp + timedelta(microseconds=1)
