from datetime import datetime, timedelta

import pytz


class TimeUtils(object):
    @staticmethod
    def utc_now_as_iso_string():
        """
        :return: Current system time in UTC in ISO 8601 string format.
        :rtype: str
        """
        return pytz.utc.localize(datetime.utcnow()).isoformat(timespec="microseconds")

    @staticmethod
    def floor_timestamp_at_resolution(dt, resolution):
        """
        Rounds the given datetime down to the nearest multiple of the specified time resolution on that date.

        :param dt: Date to floor.
        :type dt: datetime.datetime
        :param resolution: Resolution to floor to. Must be less than one day.
        :type resolution: datetime.timedelta
        :return: dt floored to the nearest multiple of resolution.
        :rtype: datetime.datetime
        """
        assert resolution.total_seconds() < timedelta(days=1).total_seconds(), \
            f"Resolution {resolution} longer than 1 day"

        day = datetime(dt.year, dt.month, dt.day, tzinfo=dt.tzinfo)
        seconds_today = (dt - day).total_seconds()
        floored_seconds_today = (seconds_today // resolution.total_seconds()) * resolution.total_seconds()

        return day + timedelta(seconds=floored_seconds_today)
