from datetime import datetime

import pytz


class TimeUtils(object):
    @staticmethod
    def utc_now_as_iso_string():
        """
        :return: Current system time in UTC in ISO 8601 string format.
        :rtype: str
        """
        return pytz.utc.localize(datetime.utcnow()).isoformat()
