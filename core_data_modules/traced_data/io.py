from os import path

import jsonpickle
import time
import six

from core_data_modules.traced_data import Metadata, TracedData

if six.PY2:
    import unicodecsv as csv
if six.PY3:
    import csv

_td_type_error_string = "argument 'data' contains an element which is not of type TracedData"


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
        :param f: File to export to.
        :type f: file-like
        :param exclude_coded_with_key: Set to None to export every item in key_of_raw to Coda, or to the key of
                                       existing codes to exclude items of key_of_raw which have already been coded.
        :type exclude_coded_with_key: str | None
        """
        data = list(data)
        for td in data:
            assert isinstance(td, TracedData), _td_type_error_string

        headers = [
            "id", "owner", "data",
            "timestamp", "schemeId", "schemeName",
            "deco_codeValue", "deco_codeId", "deco_confidence", "deco_manual", "deco_timestamp", "deco_author"
        ]

        dialect = csv.excel
        dialect.delimiter = ";"

        writer = csv.DictWriter(f, fieldnames=headers, dialect=dialect, lineterminator="\n")
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
        :param f: Coda data file to import codes from.
        :type f: file-like
        :param overwrite_existing_codes: For messages which are already coded, Whether to replace those codes with
                                         new codes from the Coda datafile.
        :type overwrite_existing_codes: bool
        :return: TracedData objects with Coda data appended
        :rtype: generator of TracedData
        """
        # TODO: This function assumes there is only one code scheme.

        # TODO: Test when running on a machine set to German.
        imported_csv = csv.DictReader(f, delimiter=";")

        # Remove rows which still haven't been coded.
        coded = list(filter(lambda row: row["deco_codeValue"] != "", imported_csv))

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


class TracedDataCSVIO(object):
    @staticmethod
    def export_traced_data_iterable_to_csv(data, f, headers=None):
        """
        Writes a collection of TracedData objects to a CSV.

        Columns will be exported in the order declared in headers if that parameter is specified,
        otherwise the output order will be arbitrary.

        :param data: TracedData objects to export.
        :type data: iterable of TracedData
        :param f: File to export to.
        :type f: file-like
        :param headers: Headers to export. If this is None, all headers will be exported.
        :type headers: list of str
        """
        data = list(data)
        for td in data:
            assert isinstance(td, TracedData), _td_type_error_string

        # If headers unspecified, search data for all headers which were used
        if headers is None:
            headers = set()
            for td in data:
                for key in six.iterkeys(td):
                    headers.add(key)

        writer = csv.DictWriter(f, fieldnames=headers, lineterminator="\n")
        writer.writeheader()

        for td in data:
            row = {key: td.get(key) for key in headers}
            writer.writerow(row)

    @staticmethod
    def import_csv_to_traced_data_iterable(user, f):
        """
        Loads a CSV into new TracedData objects.

        :param user: Identifier of user running this program.
        :type user: str
        :param f: File to import from.
        :type f: file-like
        :return: TracedData objects imported from the provided file.
        :rtype: generator of TracedData
        """
        for row in csv.DictReader(f):
            yield TracedData(dict(row), Metadata(user, Metadata.get_call_location(), time.time()))


class TracedDataJsonIO(object):
    @staticmethod
    def export_traced_data_iterable_to_json(data, f, pretty_print=False):
        """
        Exports a collection of TracedData objects to a JSON file.

        The original TracedData objects which are exported by this function are fully recoverable from the emitted
        JSON using TracedDataJsonIO.import_json_to_traced_data_iterable.

        :param data: TracedData objects to export.
        :type data: iterable of TracedData
        :param f: File to export the TracedData objects to.
        :type f: file-like
        :param pretty_print: Whether to format the JSON with line breaks, indentation, and alphabetised keys.
        :type pretty_print: bool
        """
        data = list(data)
        for td in data:
            assert isinstance(td, TracedData), _td_type_error_string

        # Serialize the list of TracedData to a format which can be trivially deserialized.
        if pretty_print:
            jsonpickle.set_encoder_options("json", sort_keys=True, indent=2, separators=(", ", ": "))
        else:
            jsonpickle.set_encoder_options("json", sort_keys=True)

        f.write(jsonpickle.dumps(data))
        f.write("\n")

    @staticmethod
    def import_json_to_traced_data_iterable(f):
        """
        Imports a JSON file to TracedData objects.

        Note that the JSON file must be a serialized representation of TracedData objects in jsonpickle format
        e.g. as produced by TracedDataJsonIO.export_traced_data_iterable_to_json.

        :param f: File to import JSON from.
        :type f: file-like
        :return: TracedData objects deserialized from the JSON file.
        :rtype: generator of TracedData
        """
        return jsonpickle.decode(f.read())


class TracedDataTheInterfaceIO(object):
    @staticmethod
    def _format_col(td, col):
        if col is None:
            return "NA"
        else:
            value = td.get(col, None)
            if value is None:
                value = "NA"
            return value

    age_groups = {
        (0, 14): "<15",
        (15, 19): "15-19",
        (20, 24): "20-24",
        (25, 29): "25-29",
        (30, 100): "30+"
    }

    @classmethod
    def export_traced_data_iterable_to_the_interface(cls, data, export_directory,
                                                     phone_col, message_col, gender_col=None,
                                                     age_col=None, county_col=None):
        data = list(data)
        for td in data:
            assert isinstance(td, TracedData), _td_type_error_string

        # Export inbox file
        with open(path.join(export_directory, "inbox"), "w") as f:
            headers = ["phone", "date", "time", "message"]

            writer = csv.DictWriter(f, fieldnames=headers, delimiter="\t")
            writer.writeheader()

            for td in data:
                row = {
                    "phone": td[phone_col],
                    "message": td[message_col]
                }

                writer.writerow(row)

        # Export demo file
        with open(path.join(export_directory, "demo"), "w") as f:
            headers = ["phone", "gender", "age", "county"]

            writer = csv.DictWriter(f, fieldnames=headers, delimiter="\t")
            writer.writeheader()

            for td in data:
                row = {
                    "phone": td[phone_col],
                    "gender": cls._format_col(td, gender_col),
                    "age": cls._format_col(td, age_col),
                    "county": cls._format_col(td, county_col)
                }

                # TODO: Pull this block out somewhere?
                if row["age"] != "NA":
                    for age_range in cls.age_groups:
                        if age_range[0] < row["age"] < age_range[1]:
                            row["age"] = cls.age_groups[age_range]
                            break
                    # TODO: What happens if we make it this far?

                writer.writerow(row)

