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
    def __init__(self, scheme_id=1, scheme_name="default", code_names=None, add_codes_for_missing=True):
        """
        :param codes: Names of codees this scheme should contain
        :type codes: iterable of str
        """
        self.scheme_id = scheme_id
        self.scheme_name = scheme_name

        if code_names is None:
            code_names = []
        code_names = list(code_names)

        if add_codes_for_missing:
            code_names.append("NC")  # TODO: Change to Codes.NOT_CODED
            code_names.append(Codes.STOP)

        self.codes = []
        next_code_id = 1
        for code_name in code_names:
            self.codes.append(Code(code_name, "{}-{}".format(scheme_id, next_code_id)))
            next_code_id += 1

    def add_code_name(self, code_name):
        pass

    def add_code(self, code, position=None):
        # TODO: Implement position (and rename to 'append_code' or 'insert_code' etc.?)
        self.codes.append(code)

    def export_to_coda_scheme_file(self, f):
        """
        Exports this CodeScheme object to a CSV which can be uploaded to Coda.

        Note: This exporter does not support versions of Coda older than "vE42857 at 2018-06-26 11:47"  # TODO: Re-release Coda and update

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
