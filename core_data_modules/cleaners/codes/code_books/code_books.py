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
    def apply_code_book_to_code(cls, code_book, code):
        """
        Converts the given code to an integer using the given code book, or the CodeBooks.MISSING code book if 
        the code is a form of missing or stop code.
        
        If the provided code is not in the code book and is not a missing/stop code, raises an AssertionError.

        >>> CodeBooks.apply_code_book_to_code(CodeBooks.YES_NO, Codes.YES)
        2
        >>> CodeBooks.apply_code_book_to_code(CodeBooks.YES_NO, Codes.TRUE_MISSING)
        -10

        :param code_book: Code book to lookup 'code' in.
        :type code_book: dict of str -> number
        :param code: Code to look up in 'code_book'.
        :type code: str
        :return: Integer for this code.
        :rtype: number
        """
        if code in code_book:
            return code_book[code]
        elif code in cls.MISSING:
            return cls.MISSING[code]
        else:
            assert False, "Code '{}' not in the provided code book or in CodeBooks.MISSING".format(code)

    @classmethod
    def apply_code_books_to_traced_data_iterable(cls, user, data, code_books):
        """
        Applies the given code books to an iterable of TracedData.

        :param user: Identifier of the user running this program, for TracedData Metadata.
        :type user: str
        :param data: TracedData objects to apply code_books to.
        :type data: iterable of TracedData
        :param code_books: Dictionary of keys of coded values to code books.
        :type code_books: dict of str -> (dict of str -> number)
        """
        for td in data:
            code_book_dict = dict()
            for coded_key, code_book in code_books.items():
                code_book_dict[coded_key] = cls.apply_code_book_to_code(code_book, td[coded_key])
            td.append_data(code_book_dict, Metadata(user, Metadata.get_call_location(), time.time()))
