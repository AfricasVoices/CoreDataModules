import unittest

from core_data_modules.cleaners import Codes
from core_data_modules.traced_data import Metadata, TracedData
from core_data_modules.util.consent_utils import ConsentUtils


class TestConsentUtils(unittest.TestCase):
    @staticmethod
    def generate_test_data():
        data_dicts = [
            {"x": "abc", "y": "def"},
            {"x": Codes.STOP, "y": "def"},
            {"x": Codes.STOP, "y": Codes.STOP},
            {"x": "abc", "y": Codes.STOP},
            {"consent_withdrawn": Codes.TRUE, "x": "efg", "y": "xyz"},
            {"consent_withdrawn": Codes.FALSE, "x": "abc", "y": "def"}
        ]

        data = [TracedData(d, Metadata("test_user", Metadata.get_call_location(), i))
                for i, d in enumerate(data_dicts)]

        return data

    def test_determine_consent_withdrawn(self):
        data = self.generate_test_data()
        ConsentUtils.determine_consent_withdrawn("test_user", data, {"x"})

        self.assertDictEqual(dict(data[0].items()), {"x": "abc", "y": "def"})
        self.assertDictEqual(dict(data[1].items()), {"consent_withdrawn": Codes.TRUE, "x": Codes.STOP, "y": "def"})
        self.assertDictEqual(dict(data[2].items()), {"consent_withdrawn": Codes.TRUE, "x": Codes.STOP, "y": Codes.STOP})
        self.assertDictEqual(dict(data[3].items()), {"x": "abc", "y": Codes.STOP})
        self.assertDictEqual(dict(data[4].items()), {"consent_withdrawn": Codes.TRUE, "x": "efg", "y": "xyz"})
        self.assertDictEqual(dict(data[5].items()), {"consent_withdrawn": Codes.FALSE, "x": "abc", "y": "def"})

    def test_set_stopped(self):
        data = self.generate_test_data()
        ConsentUtils.determine_consent_withdrawn("test_user", data, {"x"})
        ConsentUtils.set_stopped("test_user", data)

        self.assertDictEqual(dict(data[0].items()), {"x": "abc", "y": "def"})
        self.assertDictEqual(dict(data[1].items()), {"consent_withdrawn": Codes.TRUE, "x": Codes.STOP, "y": Codes.STOP})
        self.assertDictEqual(dict(data[2].items()), {"consent_withdrawn": Codes.TRUE, "x": Codes.STOP, "y": Codes.STOP})
        self.assertDictEqual(dict(data[3].items()), {"x": "abc", "y": Codes.STOP})
        self.assertDictEqual(dict(data[4].items()), {"consent_withdrawn": Codes.TRUE, "x": Codes.STOP, "y": Codes.STOP})
        self.assertDictEqual(dict(data[5].items()), {"consent_withdrawn": Codes.FALSE, "x": "abc", "y": "def"})
