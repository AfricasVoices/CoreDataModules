import json
import time

import jsonpickle
import unicodecsv
from core_data_modules import Metadata


class TracedDataCodaIO(object):
    @staticmethod
    def export_traced_data_iterable_to_coda(data, key_of_raw, f, exclude_coded_with_key=None):
        """
        Exports the elements from a "column" in a collection of TracedData objects to a file in Coda's data format.

        Optionally exports only the elements which have not yet been coded.

        :param data: TracedData objects to export data to Coda from.
        :type data: iterable of TracedData
        :param key_of_raw: The key in each TracedData object which should have its values exported (i.e. the key of the
                           messages before they were coded).
        :type key_of_raw: str
        :param f: File to export to, opened in 'wb' mode.
        :type f: file-like
        :param exclude_coded_with_key: Set to None to export every item in key_of_raw to Coda, or to the key of
                                       existing codes to exclude items of key_of_raw which have already been coded.
        :type exclude_coded_with_key: str | None
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

        if exclude_coded_with_key is not None:
            # Exclude data items which have been coded.
            data = filter(lambda td: td.get(exclude_coded_with_key) is None, data)

        # Deduplicate messages
        seen = set()
        unique_data = [td for td in data if not (td[key_of_raw] in seen or seen.add(td[key_of_raw]))]

        # Export each message to a row in Coda's datafile format.
        for i, td in enumerate(unique_data):
            row = {
                "id": i,
                "owner": i,
                "data": td[key_of_raw]
            }

            writer.writerow(row)

        # Ensure the output file doesn't end with a blank line.
        # TODO: Delete once the last line issue is fixed in Coda (see https://github.com/AfricasVoices/coda/issues/137)
        # TODO: Reliance on f.name will break some file-like arguments which are not files.
        file_path = f.name
        f.close()
        with open(file_path, "r") as f:
            lines = f.readlines()
        with open(file_path, "w") as f:
            lines[-1] = lines[-1].strip()
            f.writelines([item for item in lines if len(item) > 0])

    @staticmethod
    def import_coda_to_traced_data_iterable(user, data, key_of_raw, key_of_coded, f, overwrite_existing_codes=False):
        """
        Codes a "column" of a collection of TracedData objects by using the codes from a Coda data-file.

        :param user: Identifier of user running this program
        :type user: str
        :param data: TracedData objects to be coded using the Coda file.
        :type data: iterable of TracedData
        :param key_of_raw: Key in the TracedData objects of messages which should be coded.
        :type key_of_raw: str
        :param key_of_coded: Key in the TracedData objects to write imported codes to.
        :type key_of_coded: str
        :param f: Coda data file to import codes from, opened in 'rb' mode.
        :type f: file-like
        :param overwrite_existing_codes: For messages which are already coded, Whether to replace those codes with
                                         new codes from the Coda datafile.
        :type overwrite_existing_codes: bool
        :return: TracedData objects with Coda data appended
        :rtype: generator of TracedData
        """
        # TODO: This function assumes there is only one code scheme.

        # TODO: Test when running on a machine set to German.
        csv = unicodecsv.DictReader(f, delimiter=";")

        # Remove rows which still haven't been coded.
        coded = list(filter(lambda row: row["deco_codeValue"] != "", csv))

        for td in data:
            if not overwrite_existing_codes and td.get(key_of_coded) is not None:
                yield td
                continue

            code = None
            for row in coded:
                if td[key_of_raw] == row["data"]:
                    code = row["deco_codeValue"]

            td.append_data({key_of_coded: code}, Metadata(user, Metadata.get_call_location(), time.time()))

            yield td


class TracedDataJsonIO(object):
    @staticmethod
    def export_traced_data_iterable_to_json(data, f, pretty_print=False):
        """
        Exports a collection of TracedData objects to a JSON file.

        The original TracedData objects which are exported by this function are fully recoverable from the emitted
        JSON using TracedDataJsonIO.import_json_to_traced_data_iterable.

        :param data: TracedData objects to export.
        :type data: iterable of TracedData
        :param f: File to export the TracedData objects to, opened in "wb" mode.
        :type f: file-like
        :param pretty_print: Whether to format the JSON with new lines, indentation, and alphabetised keys.
        :type pretty_print: bool
        """
        # Serialize the list of TracedData to a format which can be trivially deserialized.
        output = jsonpickle.dumps(data)

        if pretty_print:
            # jsonpickle doesn't support pretty-printing so use the built-in json library.
            # The built-in json library was inappropriate for the initial serialization because the produced JSON is
            # not easily deserializable.
            # separators are set to account for the difference in defaults between Python 2 and Python 3
            output = json.dumps(json.loads(output), indent=2, sort_keys=True, separators=(", ", ": ")).encode()

        # Write pretty-printed JSON to a file.
        f.write(output)
        f.write("\n".encode())

    @staticmethod
    def import_json_to_traced_data_iterable(f):
        """
        Imports a JSON file to TracedData objects.

        Note that the JSON file must be a serialized representation of TracedData objects in jsonpickle format
        e.g. as produced by TracedDataJsonIO.export_traced_data_iterable_to_json.

        :param f: File to import JSON from, opened in "rb" mode.
        :type f: file-like
        :return: TracedData objects deserialized from the JSON file.
        :rtype: generator of TracedData
        """
        return jsonpickle.decode(f.read())
