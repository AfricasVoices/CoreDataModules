import time

from core_data_modules.cleaners import Codes
from core_data_modules.traced_data import Metadata


class CodeBooks(object):
    TRUE_FALSE = {
        Codes.TRUE: 1,
        Codes.FALSE: 2
    }

    GENDER = {
        Codes.MALE: 1,
        Codes.FEMALE: 2
    }

    YES_NO = {
        Codes.NO: 1,
        Codes.YES: 2
    }

    URBAN_RURAL = {
        Codes.RURAL: 1,
        Codes.URBAN: 2
    }

    MISSING = {
        Codes.TRUE_MISSING: -10,
        Codes.SKIPPED: -20,
        Codes.NOT_CODED: -30,
        Codes.NOT_REVIEWED: -40,
        Codes.NOT_LOGICAL: -50,

        Codes.STOP: Codes.STOP
    }

    @classmethod
    def apply_code_book(cls, code_book, code):
        if code in code_book:
            return code_book[code]
        elif code in cls.MISSING:
            return cls.MISSING[code]
        else:
            assert False, "Code '{}' not in the provided code book or in CodeBooks.MISSING".format(code)

    @classmethod
    def apply_missing_code_book(cls, code):
        return cls.apply_code_book(dict(), code)

    @classmethod
    def apply(cls, user, data, code_books):
        for td in data:
            code_book_dict = dict()
            for coded_key, code_book in code_books.items():
                code_book_dict[coded_key] = cls.apply_code_book(code_book, td[coded_key])
            td.append_data(code_book_dict, Metadata(user, Metadata.get_call_location(), time.time()))
