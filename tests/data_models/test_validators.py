import unittest

from core_data_modules.data_models import validators


class TestValidators(unittest.TestCase):
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
