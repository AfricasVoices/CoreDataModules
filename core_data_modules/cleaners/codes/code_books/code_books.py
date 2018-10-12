from core_data_modules.cleaners import Codes


class CodeBooks(object):
    urban_rural = {
        Codes.RURAL: 1,
        Codes.URBAN: 2
    }

    yes_no = {
        Codes.NO: 1,
        Codes.YES: 2
    }

    gender = {
        Codes.MALE: 1,
        Codes.FEMALE: 2
    }

    missing = {
        Codes.TRUE_MISSING: -10,
        Codes.SKIPPED: -20,
        Codes.NOT_CODED: -30,
        Codes.NOT_REVIEWED: -40,
        Codes.NOT_LOGICAL: -50,

        Codes.STOP: Codes.STOP
    }

    @classmethod
    def apply(cls, user, data, code_books):
        pass
