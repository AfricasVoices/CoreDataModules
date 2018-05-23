import time

import unicodecsv
from core_data_modules import Metadata


class TracedDataCodaIO(object):
    @staticmethod
    def export_traced_data_iterable_to_coda(data, f, raw_key, include_coded=False, coded_key=None):
        """
        Exports the elements which have not been coded from a "column" in a collection of TracedData objects
        to a file in Coda's data format.

        :param data: TracedData objects to export data to Coda from.
        :type data: iterable of TracedData
        :param raw_key: The key in each TracedData object which should have its values exported.
        :type raw_key: str
        :param f: File to export to, opened in 'wb' mode.
        :type f: file-like
        :param include_coded: Whether to include data which has already been coded when exporting.
        :type include_coded: bool
        :param coded_key: TODO
        :type coded_key: str
        """
        headers = [
            "id", "owner", "data",
            "timestamp", "schemeId", "schemeName",
            "deco_codeValue", "deco_codeId", "deco_confidence", "deco_manual", "deco_timestamp", "deco_author"
        ]

        dialect = unicodecsv.excel
        dialect.delimiter = ";"

        writer = unicodecsv.DictWriter(f, fieldnames=headers, dialect=dialect, lineterminator="\n")
        writer.writeheader()

        if not include_coded:
            # Exclude data items which have been coded.
            data = filter(lambda td: coded_key not in td or td[coded_key] is None, data)

        # Deduplicate messages
        seen = set()
        unique_data = [td for td in data if not (td[raw_key] in seen or seen.add(td[raw_key]))]

        # Export each message to a row in Coda's datafile format.
        for i, td in enumerate(unique_data):
            row = {
                "id": i,
                "owner": i,
                "data": td[raw_key]
            }

            writer.writerow(row)

        # Ensure the output file doesn't end with a blank line.
        # TODO: Fix in Coda? This is not the first case that this issue has caused us pain.
        # TODO: Reliance on f.name will break some file-like arguments which are not files.
        file_path = f.name
        f.close()
        with open(file_path, "r") as f:
            lines = f.readlines()
        with open(file_path, "w") as f:
            lines[-1] = lines[-1].strip()
            f.writelines([item for item in lines if len(item) > 0])

    @staticmethod
    def import_coda_to_traced_data_iterable(data, raw_key, coded_key, f):
        """
        Codes a "column" of a collection of TracedData objects by looking up each value for that column in a coded
        Coda data file, and assigning the coded values to a specified column.

        :param data: TracedData objects to append import data into.
        :type data: iterable of TracedData
        :param raw_key: Key of TracedData objects which should be coded.
        :type raw_key: str
        :param coded_key: Key to write coded data to.
        :type coded_key: str
        :param f: Coda data file to import codes from.
        :type f: file-like
        :return: TracedData objects with Coda data appended
        :rtype: generator of TracedData
        """
        # TODO: This function assumes there is only one code scheme.

        # TODO: Test when running on a machine set to German.
        csv = unicodecsv.DictReader(f, delimiter=";")

        # Remove rows which still haven't been coded.
        coded = list(filter(lambda row: row["deco_codeValue"] != "", csv))

        for td in data:
            code = None

            for row in coded:
                if td[raw_key] == row["data"]:
                    code = row["deco_codeValue"]

            # TODO: Retrieve user/source from somewhere.
            td.append_data({coded_key: code}, Metadata("user", "coda_import", time.time()))

            yield td
