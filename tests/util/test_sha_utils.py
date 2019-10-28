import unittest

from core_data_modules.util import SHAUtils


class TestSHAUtils(unittest.TestCase):
    def test_sha_string(self):
        self.assertEqual(
            SHAUtils.sha_string("test"),
            "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
        )

        self.assertEqual(
            SHAUtils.sha_string(""),
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        )

    def test_sha_file_at_path(self):
        self.assertEqual(
            # 6.3 KiB file of random base64 data and new lines
            SHAUtils.sha_file_at_path("tests/util/resources/sha_test_data.txt"),

            # Sha of file computed using `$ shasum -a 256 tests/util/resources/sha_test_data.txt`
            "24244c9751746fad483dbc72a97c7d2d406dbead491c9d2e0dab26503f361c58"
        )
        
        self.assertEqual(
            # 184 KiB file of random base64 data and new lines
            SHAUtils.sha_file_at_path("tests/util/resources/sha_test_data_large.txt"),

            # Sha of file computed using `$ shasum -a 256 tests/util/resources/sha_test_data_large.txt`
            "08243b78b36b6a0e170bca6d5c9e6348e5db002dd2a5dbf3a27b25895b5859a4"
        )
