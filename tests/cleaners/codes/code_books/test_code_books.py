import unittest

from core_data_modules.cleaners import Codes
from core_data_modules.cleaners.codes.code_books import CodeBooks
from core_data_modules.traced_data import TracedData, Metadata


class TestCodeBooks(unittest.TestCase):
    def test_apply(self):
        data_dicts = [
            {"Gender": Codes.FEMALE, "Urban/Rural": Codes.RURAL},
            {"Gender": Codes.FEMALE, "Urban/Rural": Codes.URBAN},
            {"Gender": Codes.TRUE_MISSING, "Urban/Rural": Codes.RURAL},
            {"Gender": Codes.MALE, "Urban/Rural": Codes.NOT_CODED}
        ]

        data = [TracedData(d, Metadata("test_user", Metadata.get_call_location(), i))
                for i, d in enumerate(data_dicts)]

        code_books = {
            "Gender": CodeBooks.GENDER,
            "Urban/Rural": CodeBooks.URBAN_RURAL
        }

        CodeBooks.apply("test_user", data, code_books)

        self.assertDictEqual(dict(data[0].items()), {"Gender": 2, "Urban/Rural": 1})
        self.assertDictEqual(dict(data[1].items()), {"Gender": 2, "Urban/Rural": 2})
        self.assertDictEqual(dict(data[2].items()), {"Gender": -10, "Urban/Rural": 1})
        self.assertDictEqual(dict(data[3].items()), {"Gender": 1, "Urban/Rural": -30})
