from core_data_modules.cleaners import Codes


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
    def apply(cls, user, data, code_books):
        pass
