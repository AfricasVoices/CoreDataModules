import six

from core_data_modules.cleaners import Codes

if six.PY2:
    import unicodecsv as csv
if six.PY3:
    import csv


class Code(object):
    def __init__(self, name, id):
        self.name = name
        self.id = id


class CodeScheme(object):
    def __init__(self, scheme_id=1, scheme_name="default", code_names=None):
        """
        :param codes: Names of codees this scheme should contain
        :type codes: iterable of str
        """
        self.scheme_id = scheme_id
        self.scheme_name = scheme_name

        self.codes = []
        if code_names is None:
            code_names = []
        next_code_id = 1
        for code_name in code_names:
            self.codes.append(Code(code_name, "{}-{}".format(scheme_id, next_code_id)))
            next_code_id += 1

    @classmethod
    def with_missing_codes(cls, code_names, scheme_id=1, scheme_name="default"):
        code_names = list(code_names)
        code_names.append("NC")  # TODO: Change to Codes.NOT_CODED
        code_names.append(Codes.STOP)

        return cls(scheme_id=scheme_id, scheme_name=scheme_name, code_names=code_names)

    def export_to_coda_scheme_file(self, f):
        """
        Exports this CodeScheme object to a CSV which can be uploaded to Coda.

        :param f: File to write code scheme to.
        :type f: file-like
        """
        headers = ["scheme_id", "scheme_name", "code_id", "code_value", "code_colour", "code_shortcut",
                   "code_words", "code_regex", "code_regex_modifier"]

        dialect = csv.excel
        dialect.delimiter = ";"

        writer = csv.DictWriter(f, fieldnames=headers, dialect=dialect, lineterminator="\n")
        writer.writeheader()

        for code in self.codes:
            writer.writerow({
                "scheme_id": self.scheme_id,
                "scheme_name": self.scheme_name,
                "code_id": code.id,
                "code_value": code.name,
                "code_colour": "",
                "code_shortcut": "",
                "code_words": "",
                "code_regex": "",
                "code_regex_modifier": ""
            })
