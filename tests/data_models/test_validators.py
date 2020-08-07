import unittest

from dateutil.parser import isoparse

from core_data_modules.data_models import validators


class TestValidators(unittest.TestCase):
    def test_validate_datetime(self):
        dt = isoparse("2019-05-10T12:37:04+03:00")
        self.assertEqual(dt, validators.validate_datetime(dt))

        with self.assertRaisesRegex(AssertionError, "dt not a datetime"):
            validators.validate_datetime("2019-05-10T12:37:04+03:00", "dt")

        with self.assertRaisesRegex(AssertionError, "dt not timezone-aware"):
            validators.validate_datetime(isoparse("2019-05-10T12:37:04"), "dt")

    def test_validate_url(self):
        # Test valid URLs
        valid_urls = [
            "https://www.africasvoices.org",
            "http://localhost:8080/index.html",
            "gs://bucket/path/to/blob"
        ]

        for url in valid_urls:
            self.assertEqual(url, validators.validate_url(url))

        # Test invalid URLs
        with self.assertRaisesRegex(AssertionError, "test_url not a valid URL"):
            validators.validate_url("abc://[", variable_name="test_url")

        with self.assertRaisesRegex(AssertionError, " not a URL with scheme gs"):
            validators.validate_url("http://bucket/blob", scheme="gs")
