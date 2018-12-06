# coding=utf-8
import unittest

from core_data_modules.data_models import validators


class TestValidators(unittest.TestCase):
    def _expect_validation_failure(self, f, expected_assertion_error_message):
        try:
            f()
        except AssertionError as e:
            assert str(e) == expected_assertion_error_message
            return

        self.fail("Invalid data passed validation")

    def test_validate_string(self):
        validators.validate_string("Test")
        validators.validate_string("åø")

        self._expect_validation_failure(lambda: validators.validate_string(4), " not a string")
        
    def test_validate_iso_string(self):
        validators.validate_iso_string("2018")
        validators.validate_iso_string("2018-11-10T13:00:00")
        validators.validate_iso_string("2018-11-10T13:00Z")
        validators.validate_iso_string("2018-11-10T13:00:05+00:00")
        validators.validate_iso_string("2018-11-10T13:00:05+03:00")

        self._expect_validation_failure(lambda: validators.validate_iso_string("5/12/2018"), " not an ISO string")
        self._expect_validation_failure(lambda: validators.validate_iso_string("05/12/2018"), " not an ISO string")
        self._expect_validation_failure(lambda: validators.validate_iso_string("2018-11-1013:00"), " not an ISO string")

    def test_validate_utc_iso_string(self):
        validators.validate_utc_iso_string("2018-11-10T13:00:05Z")
        validators.validate_utc_iso_string("2018-11-10T13:00:05+00:00")

        self._expect_validation_failure(
            lambda: validators.validate_utc_iso_string("2018-11-10T13:00:00"), " not a UTC ISO string")

        self._expect_validation_failure(
            lambda: validators.validate_utc_iso_string("2018-11-10T13:00:05+03:00"), " not a UTC ISO string")
