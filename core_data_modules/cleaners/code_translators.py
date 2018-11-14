from core_data_modules.cleaners import Codes


class GenderTranslator(object):
    # TODO: Assert these codes are in sync with Standards?
    # TODO: e.g. by asserting that a scheme version listed here matches that in the gender_scheme json file?
    SCHEME_ID = "Scheme-12cb6f95"
    _LUT = {
        Codes.MALE: "code-63dcde9a",
        Codes.FEMALE: "code-86a4602c",

        Codes.TRUE_MISSING: "code-NA-3498451d",
        Codes.SKIPPED: "code-NS-5334289d",
        Codes.NOT_CODED: "code-NC-11d6bb91",
        Codes.NOT_REVIEWED: "code-NR-03dd5d73"
    }

    @classmethod
    def code_id(cls, code):
        return cls._LUT[code]
