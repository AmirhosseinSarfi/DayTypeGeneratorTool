import math


def timeBucketNumber(timeResolution):
    """
    Function that returns the number of time buckets within a day given the time resolution, expressed in minutes,
    of the time series. It is assumed that the time series are defined of a perfect time grid of such input
    time resolution.
    """
    buckets = math.ceil(1440.0 / timeResolution)  # 1440 minutes in 24h

    return buckets
