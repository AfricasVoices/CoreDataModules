from core_data_modules.cleaners import Codes


class CodeScheme(object):
    def __init__(self, codes):
        """
        :param codes: Names of codees this scheme should contain
        :type codes: iterable of str
        """
        self._codes = list(codes)

    @classmethod
    def with_missing_codes(cls, codes):
        codes = list(codes)
        codes.append("NC")  # TODO: Change to Codes.NOT_CODED
        codes.append(Codes.STOP)

        return cls(codes)

    def export_to_coda_scheme_file(self, f):
        pass
