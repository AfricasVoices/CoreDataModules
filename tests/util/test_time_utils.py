import unittest

from core_data_modules.util import TimeUtils


class TestTimeUtils(unittest.TestCase):
    def test_iso_string_to_epoch_seconds(self):
        self.assertEqual(TimeUtils.iso_string_to_epoch_seconds("1970-01-01T00:00:00Z"), 0)
        self.assertEqual(TimeUtils.iso_string_to_epoch_seconds("1970-01-01T03:00:00+03:00"), 0)

        self.assertEqual(TimeUtils.iso_string_to_epoch_seconds("2018-12-12T11:42:20+00:00"), 1544614940)
        self.assertEqual(TimeUtils.iso_string_to_epoch_seconds("2018-12-12T14:42:20.223+03:00"), 1544614940.223)
