import unittest
from datetime import timedelta

from dateutil.parser import isoparse

from core_data_modules.util import TimeUtils


class TestTimeUtils(unittest.TestCase):
    def test_datetime_to_utc_iso_string(self):
        # Test utc datetime.
        self.assertEqual(
            TimeUtils.datetime_to_utc_iso_string(isoparse("2021-05-30T13:46:00.123456Z")),
            "2021-05-30T13:46:00.123456+00:00"
        )

        # Test utc datetime with trailing zeros.
        self.assertEqual(
            TimeUtils.datetime_to_utc_iso_string(isoparse("2021-05-30T13:46:00.123000Z")),
            "2021-05-30T13:46:00.123000+00:00"
        )

        # Test utc+3h datetime.
        self.assertEqual(
            TimeUtils.datetime_to_utc_iso_string(isoparse("2021-05-30T16:46:00.123456+03:00")),
            "2021-05-30T13:46:00.123456+00:00"
        )

    def test_floor_timestamp_at_resolution(self):
        self.assertEqual(
            TimeUtils.floor_timestamp_at_resolution(isoparse("2019-05-04T13:46:17.123456Z"), timedelta(minutes=10)),
            isoparse("2019-05-04T13:40Z")
        )

        self.assertEqual(
            TimeUtils.floor_timestamp_at_resolution(isoparse("2019-05-04T13:46:17.123456Z"), timedelta(hours=2)),
            isoparse("2019-05-04T12:00Z")
        )

        with self.assertRaisesRegex(AssertionError, "Resolution (.*) longer than 1 day"):
            TimeUtils.floor_timestamp_at_resolution(isoparse("2000-01-01T12:00"), timedelta(days=3))
