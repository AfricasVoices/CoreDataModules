from datetime import datetime

import pytz
from dateutil.parser import isoparse


class TimeUtils(object):
    @staticmethod
    def utc_now_as_iso_string():
        """
        :return: Current system time in UTC in ISO 8601 string format.
        :rtype: str
        """
        return pytz.utc.localize(datetime.utcnow()).isoformat()

    @staticmethod
    def iso_string_to_epoch_seconds(iso_string):
        """
        Converts an ISO 8601 string to a timestamp that represents the number of seconds since the UNIX epoch
        (Jan 1st 1970 UTC).

        :param iso_string: ISO 8601 format string to convert.
        :type iso_string: str
        :return: Timestamp in seconds since the UNIX epoch.
        :rtype: float
        """
        return (isoparse(iso_string) - datetime(1970, 1, 1, tzinfo=pytz.utc)).total_seconds()
