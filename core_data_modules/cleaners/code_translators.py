from core_data_modules.cleaners import Codes


class CodeTranslator(object):
    def __init__(self, scheme_id, code_id_lut):
        self.scheme_id = scheme_id
        self.code_id_lut = code_id_lut

    def code_id(self, code):
        return self.code_id_lut[code]


GenderTranslator = CodeTranslator("Scheme-12cb6f95", {
    Codes.MALE: "code-63dcde9a",
    Codes.FEMALE: "code-86a4602c",

    Codes.TRUE_MISSING: "code-NA-3498451d",
    Codes.SKIPPED: "code-NS-5334289d",
    Codes.NOT_CODED: "code-NC-11d6bb91",
    Codes.NOT_REVIEWED: "code-NR-03dd5d73"
})
