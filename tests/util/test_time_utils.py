import unittest
from datetime import timedelta

from dateutil.parser import isoparse

from core_data_modules.util import TimeUtils


class TestTimeUtils(unittest.TestCase):
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
