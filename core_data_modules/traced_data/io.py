import time
from datetime import datetime
from os import path

import jsonpickle
import six
from dateutil.parser import isoparse

from core_data_modules.traced_data import Metadata, TracedData

if six.PY2:
    import unicodecsv as csv
if six.PY3:
    import csv

_td_type_error_string = "argument 'data' contains an element which is not of type TracedData"


class _TracedDataIOUtil(object):
    """
    A collection of utility functions used by the IO classes in this file.
    
    Not for external use.
    """

    @staticmethod
    def unique_messages(data, key_of_raw):
        """
        Filters a collection of TracedData objects such that there is only one object with each value for the given key.
        
        If there are multiple TracedData objects with the same value for the given key, one of those will be selected
        arbitrarily; the rest will be dropped.
        
        :param data: TracedData objects to select unique messages from.
        :type data: iterable of TracedData
        :param key_of_raw: Key in TracedData objects of raw messages which should be unique in output.
        :type key_of_raw: str
        :return: TracedData objects distinct by the given key.
        :rtype: list of TracedData
        """
        seen = set()
        unique_data = []
        for td in data:
            if not td[key_of_raw] in seen:
                seen.add(td[key_of_raw])
                unique_data.append(td)
                
        return unique_data

    @staticmethod
    def assert_uniquely_coded(data, key_of_raw, key_of_coded):
        """
        Ensures that all messages which are the same for a given key have been given exactly the same codes.

        Raises an AssertionError if there are identical messages that have been coded differently in the dataset.

        :param data: TracedData objects to check are uniquely coded.
        :type data: iterable of TracedData
        :param key_of_raw: Key in TracedData objects of raw messages.
        :type key_of_raw: str
        :param key_of_coded: Key in TracedData objects of the codes which have been applied to the messages.
        :type key_of_coded: str
        """
        seen = dict()
        for td in data:
            if not td[key_of_raw] in seen:
                seen[td[key_of_raw]] = td.get(key_of_coded)
            else:
                assert seen[td[key_of_raw]] == td.get(key_of_coded), \
                    "Raw message '{}' not uniquely coded.".format(td[key_of_raw])

    @staticmethod
    def exclude_coded_with_key(data, key):
        """
        Filters a collection of TracedData objects such that only objects which do not have codes under the given 
        key are returned.

        :param data: TracedData objects to filter.
        :type data: iterable of TracedData
        :param key: Key in TracedData objects of codes.
        :type key: str
        :return: TracedData objects which have not been coded under the given key.
        :rtype: iterable of TracedData
        """
        return filter(lambda td: td.get(key) is None, data)


class TracedDataCodaIO(object):
    @staticmethod
    def _generate_new_coda_id(existing_ids):
        for i in range(1, 100):
            if i not in existing_ids:
                return i
        assert False, "Unable to generate a new Coda id. Report this error to the project developers."

    @staticmethod
    def export_traced_data_iterable_to_coda(data, key_of_raw, f, exclude_coded_with_key=None):
        """
        Exports the elements from a "column" in a collection of TracedData objects to a file in Coda's data format.

        This function does not export existing codes. For this, use
        TracedDataCodaIO.export_traced_data_iterable_to_coda_with_codes.

        Optionally exports only the elements which have not yet been coded, using the exclude_coded_with_key parameter.

        Note: This exporter does not support versions of Coda older than "vE42857 at 2018-06-26 11:47"

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
            "deco_codeValue", "deco_codeId", "deco_confidence", "deco_codingMode", "deco_timestamp", "deco_author"
        ]

        dialect = csv.excel
        dialect.delimiter = ";"

        writer = csv.DictWriter(f, fieldnames=headers, dialect=dialect, lineterminator="\n")
        writer.writeheader()

        if exclude_coded_with_key is not None:
            # Exclude data items which have been coded.
            data = _TracedDataIOUtil.exclude_coded_with_key(data, exclude_coded_with_key)

        # De-duplicate raw messages
        unique_data = _TracedDataIOUtil.unique_messages(data, key_of_raw)

        # Export each message to a row in Coda's datafile format.
        for i, td in enumerate(unique_data):
            row = {
                "id": i,
                "owner": i,
                "data": td[key_of_raw]
            }

            writer.writerow(row)

    @classmethod
    def export_traced_data_iterable_to_coda_with_scheme(cls, data, key_of_raw, scheme_keys, f, prev_f=None):
        """
        Exports the elements from a "column" in a collection of TracedData objects to a file in Coda's data format.
        
        This function exports a code scheme to Coda. To export raw messages only, use
        TracedDataCodaIO.export_traced_data_iterable_to_coda.

        Note: This exporter does not support versions of Coda older than "vE42857 at 2018-06-26 11:47"

        :param data: TracedData objects to export data to Coda from.
        :type data: iterable of TracedData
        :param key_of_raw: The key in each TracedData object which should have its values exported (i.e. the key of the
                           messages before they were coded).
        :type key_of_raw: str
        :param scheme_keys: Dictionary of Coda scheme name to the key in each TracedData object of existing codes.
                            TracedData objects missing that key will have their raw value exported, but no pre-existing
                            code.
        :type scheme_keys: dict of str -> str
        :param f: File to export to.
        :type f: file-like
        :param prev_f: An optional previous version of the Coda file. If this argument is provided, the referenced file
                       will be copied to the output file 'f', then any new data/codes will be appended.
                       No edits are made to any of the items which are copied through to 'f'.
        :type prev_f: file-like | None.
        """
        data = list(data)
        for td in data:
            assert isinstance(td, TracedData), _td_type_error_string

        headers = [
            "id", "owner", "data",
            "timestamp", "schemeId", "schemeName",
            "deco_codeValue", "deco_codeId", "deco_confidence", "deco_codingMode", "deco_timestamp", "deco_author"
        ]

        dialect = csv.excel
        dialect.delimiter = ";"

        writer = csv.DictWriter(f, fieldnames=headers, dialect=dialect, lineterminator="\n")
        writer.writeheader()

        for key_of_coded in scheme_keys.values():
            _TracedDataIOUtil.assert_uniquely_coded(data, key_of_raw, key_of_coded)
        unique_data = _TracedDataIOUtil.unique_messages(data, key_of_raw)

        # Export each message to a row in Coda's datafile format.
        scheme_ids = dict()  # of scheme name -> scheme id
        code_ids = dict()  # of scheme name -> (dict of code -> code id)
        item_id = 0

        if prev_f is not None:
            # Read the previously coded Coda file
            prev_rows = list(csv.DictReader(prev_f, delimiter=";"))

            # Exclude items in unique_data which are in the previously coded file.
            prev_data = set(map(lambda row: row["data"], prev_rows))
            unique_data = [td for td in unique_data if td[key_of_raw] not in prev_data]

            # Rebuild scheme_ids dict from the previously coded file.
            scheme_ids = {row["schemeName"]: row["schemeId"] for row in prev_rows if row["schemeId"] != ""}

            # Rebuild code_ids dict from the previously coded file.
            for row in prev_rows:
                prev_scheme_name = row["schemeName"]
                prev_code_value = row["deco_codeValue"]
                prev_code_id = row["deco_codeId"]

                if prev_code_value == "":
                    continue

                if prev_scheme_name not in code_ids:
                    code_ids[prev_scheme_name] = dict()

                scheme_code_ids = code_ids[prev_scheme_name]
                if prev_code_value not in scheme_code_ids:
                    scheme_code_ids[prev_code_value] = prev_code_id
                else:
                    assert scheme_code_ids[prev_code_value] == row["deco_codeId"]

            # Detect the highest row/owner ids in the previously coded file. New row ids will increment from these.
            max_prev_item_id = 0
            for row in prev_rows:
                max_prev_item_id = max(max_prev_item_id, int(row["id"]))
            item_id = max_prev_item_id + 1

            # Write the contents of the previously coded file through to the new output file.
            for row in prev_rows:
                writer.writerow(row)

        # Populate scheme_ids dict
        for scheme_name, key_of_coded in scheme_keys.items():
            if scheme_name not in scheme_ids:
                scheme_ids[scheme_name] = cls._generate_new_coda_id(scheme_ids.values())

        for td in unique_data:
            for scheme_name, key_of_coded in scheme_keys.items():
                row = {
                    "id": item_id,
                    "owner": item_id,
                    "data": td[key_of_raw],

                    "schemeId": scheme_ids[scheme_name],
                    "schemeName": scheme_name
                    # Not exporting timestamp because this doesn't actually do anything in Coda.
                }

                # If this item has been coded under each scheme, export that code.
                code = td.get(key_of_coded, None)

                if scheme_name not in code_ids:
                    code_ids[scheme_name] = dict()
                scheme_code_ids = code_ids[scheme_name]

                if code is not None:
                    if code not in scheme_code_ids:
                        # Note: This assumes Coda code ids always take the form '<scheme-id>-<code-id>'
                        new_code_id = cls._generate_new_coda_id([int(id.split("-")[1]) for id in scheme_code_ids.values()])
                        new_scheme_code_id = "{}-{}".format(scheme_ids[scheme_name], new_code_id)
                        assert new_scheme_code_id not in scheme_code_ids.values(), \
                            "Failed to generate a new, unique code id for code '{}'".format(code)
                        scheme_code_ids[code] = new_scheme_code_id

                    row.update({
                        "deco_codeValue": code,
                        "deco_codeId": scheme_code_ids[code],
                        "deco_confidence": 0.95,  # Same confidence as auto-coding in Coda as of ve42857.
                        "deco_codingMode": "external",
                        # Not exporting deco_timestamp or deco_author because Coda just overwrites them
                        # (on load and save respectively), and neither is used anyway.
                    })

                writer.writerow(row)
            item_id += 1

    @staticmethod
    def import_coda_to_traced_data_iterable(user, data, key_of_raw, scheme_keys, f, overwrite_existing_codes=False):
        """
        Codes a "column" of a collection of TracedData objects by using the codes from a Coda data-file.

        :param user: Identifier of user running this program
        :type user: str
        :param data: TracedData objects to be coded using the Coda file.
        :type data: iterable of TracedData
        :param key_of_raw: Key in the TracedData objects of messages which should be coded.
        :type key_of_raw: str
        :param scheme_keys: Dictionary of Coda scheme name to the key in each TracedData object of coded data
                            for that scheme.
        :type scheme_keys: dict of str -> str
        :param f: Coda data file to import codes from.
        :type f: file-like
        :param overwrite_existing_codes: For messages which are already coded, whether to replace those codes with
                                         new codes from the Coda datafile.
        :type overwrite_existing_codes: bool
        """
        # TODO: Test when running on a machine set to German.
        imported_csv = csv.DictReader(f, delimiter=";")

        # Remove rows which still haven't been coded.
        coded = list(filter(lambda row: row["deco_codeValue"] != "", imported_csv))

        for td in data:
            for scheme_name, key_of_coded in scheme_keys.items():
                if not overwrite_existing_codes and td.get(key_of_coded) is not None:
                    continue

                code = None
                for row in coded:
                    if td[key_of_raw] == row["data"] and row["schemeName"] == scheme_name:
                        code = row["deco_codeValue"]

                td.append_data({key_of_coded: code}, Metadata(user, Metadata.get_call_location(), time.time()))


class TracedDataCodingCSVIO(object):
    @staticmethod
    def export_traced_data_iterable_to_coding_csv(data, key_of_raw, f, exclude_coded_with_key=None):
        """
        Exports the elements from a "column" in a collection of TracedData objects to a CSV file for coding.

        This function does not export existing codes. For this, use
        TracedDataCodingCSVIO.export_traced_data_iterable_to_coding_csv_with_codes.

        Optionally exports only the elements which have not yet been coded, using the exclude_coded_with_key parameter.

        :param data: TracedData objects to export data to a CSV from.
        :type data: iterable of TracedData
        :param key_of_raw: The key in each TracedData object which should have its values exported (i.e. the key of the
                           messages before they were coded).
        :type key_of_raw: str
        :param f: File to export to.
        :type f: file-like
        :param exclude_coded_with_key: Set to None to export every item in key_of_raw, or to the key of
                                       existing codes to exclude items of key_of_raw which have already been coded.
        :type exclude_coded_with_key: str | None
        """
        data = list(data)
        for td in data:
            assert isinstance(td, TracedData), _td_type_error_string

        if exclude_coded_with_key is not None:
            # Exclude data items which have been coded.
            data = _TracedDataIOUtil.exclude_coded_with_key(data, exclude_coded_with_key)

        # De-duplicate raw messages
        unique_data = _TracedDataIOUtil.unique_messages(data, key_of_raw)

        TracedDataCSVIO.export_traced_data_iterable_to_csv(unique_data, f, headers=[key_of_raw])

    @staticmethod
    def export_traced_data_iterable_to_coding_csv_with_scheme(data, key_of_raw, key_of_coded, f):
        """
        Exports the elements from a "column" in a collection of TracedData objects to a CSV file for coding.

        This function exports a code scheme to Coda. To export raw messages only, use
        TracedDataCodingCSVIO.export_traced_data_iterable_to_coda.

        :param data: TracedData objects to export data to a coding CSV from.
        :type data: iterable of TracedData
        :param key_of_raw: The key in each TracedData object which should have its values exported (i.e. the key of the
                           messages before they were coded).
        :type key_of_raw: str
        :param key_of_coded: The key in each TracedData object of the codes which have been applied to the messages.
        :type key_of_coded: str
        :param f: File to export to.
        :type f: file-like
        """
        data = list(data)
        for td in data:
            assert isinstance(td, TracedData), _td_type_error_string

        _TracedDataIOUtil.assert_uniquely_coded(data, key_of_raw, key_of_coded)
        unique_data = _TracedDataIOUtil.unique_messages(data, key_of_raw)

        TracedDataCSVIO.export_traced_data_iterable_to_csv(unique_data, f, headers=[key_of_raw, key_of_coded])

    @staticmethod
    def import_coding_csv_to_traced_data_iterable(user, data, key_of_raw_in_data, key_of_coded_in_data,
                                                  key_of_raw_in_f, key_of_coded_in_f,
                                                  f, overwrite_existing_codes=False):
        """
        Codes a "column" of a collection of TracedData objects by using the codes from a Coding CSV file.

        :param user: Identifier of user running this program
        :type user: str
        :param data: TracedData objects to be coded using the Coda file.
        :type data: iterable of TracedData
        :param key_of_raw_in_data: Key in the TracedData objects of messages which should be coded.
        :type key_of_raw_in_data: str
        :param key_of_coded_in_data: Key in the TracedData objects to write imported codes to.
        :type key_of_coded_in_data: str
        :param key_of_raw_in_f: Name of column header in f of raw messages.
        :type key_of_raw_in_f: str
        :param key_of_coded_in_f: Name of column header in f of codes.
        :type key_of_coded_in_f: str
        :param f: Coding CSV file to import codes from.
        :type f: file-like
        :param overwrite_existing_codes: For messages which are already coded, whether to replace those codes with
                                         new codes from the coding CSV file.
        :type overwrite_existing_codes: bool
        :return: TracedData objects with the coding CSV data appended
        :rtype: generator of TracedData
        """
        # TODO: This function assumes there is only one code scheme.

        imported_csv = TracedDataCSVIO.import_csv_to_traced_data_iterable(user, f)

        # Remove rows which still haven't been coded
        coded = list(filter(lambda row: row[key_of_coded_in_f] != "", imported_csv))

        for td in data:
            if not overwrite_existing_codes and td.get(key_of_coded_in_data) is not None:
                yield td
                continue

            code = None
            for row in coded:
                if td[key_of_raw_in_data] == row[key_of_raw_in_f]:
                    code = row[key_of_coded_in_f]

            td.append_data({key_of_coded_in_data: code}, Metadata(user, Metadata.get_call_location(), time.time()))

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
    def _get_demographic(td, key):
        """
        Gets the demographic value for the given key of the given TracedData object.

        Returns "NA" if the key is None, the TracedData object doesn't have that key, or the value for that key is None.

        :param td: TracedData object to get value of.
        :type td: TracedData
        :param key: Key of TracedData object to access.
        :type key: str
        :rtype: str
        """
        if key is None:
            return "NA"
        else:
            value = td.get(key, None)
            if value is None:
                value = "NA"
            return value

    @staticmethod
    def _clean_interface_message(message):
        return CharacterCleaner.fold_lines(message)

    @staticmethod
    def _age_to_age_group(age):
        age_groups = {
            (0, 14): "<15",
            (15, 19): "15-19",
            (20, 24): "20-24",
            (25, 29): "25-29",
            (30, 100): "30+"
        }

        for age_range in age_groups:
            if age_range[0] < age < age_range[1]:
                return age_groups[age_range]
        return "NA"

    @classmethod
    def export_traced_data_iterable_to_the_interface(cls, data, export_directory,
                                                     phone_key, message_key, date_key, tag_messages=False,
                                                     gender_key=None, age_key=None, county_key=None):
        """
        Exports a collection of TracedData objects to inbox and demo files required by The Interface.
        
        :param data: TracedData objects to export.
        :type data: iterable of TracedData
        :param export_directory: Directory to write inbox and demo files to.
        :type export_directory: str
        :param phone_key: Key in TracedData objects of respondent's phone number (or id)
        :type phone_key: str
        :param message_key: Keys in the TracedData objects to export to the inbox file's "message" column.
                             Messages are cleaned before export by converting to ASCII, removing punctuation,
                             converting to lower case, and removing new line characters.
        :type message_key: str
        :param date_key: Key in TracedData objects of the date/time value to export with each inbox file entry.
                         Date/time values must be in ISO 8601 format.
                         Time zone information is ignored
                         (i.e. strings are assumed to be in local time with the local offset)
        :type date_key: str
        :param tag_messages: Whether to prepend output messages with the corresponding message_key.
        :type tag_messages: bool
        :param gender_key: Key in TracedData objects of respondent's gender.
        :type gender_key: str
        :param age_key: Key in TracedData objects of respondent's age.
                        Age entries of TracedData must be numbers.
                        They will be converted to the age ranges <15, 15-19, 20-24, 25-29, 30+, or NA.
        :type age_key: str
        :param county_key: Key in TracedData objects of respondent's county.
        :type county_key: str
        """
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
                    "phone": td[phone_key],
                    "date": datetime.strftime(isoparse(td[date_key]), "%m/%d/%Y"),
                    "time": datetime.strftime(isoparse(td[date_key]), "%H:%M:%S"),
                    "message": cls._clean_interface_message(td[message_key])
                }

                if tag_messages:
                    row["message"] = "{} {}".format(message_key, row["message"])

                writer.writerow(row)

        # Export demo file
        with open(path.join(export_directory, "demo"), "w") as f:
            headers = ["phone", "gender", "age", "county"]

            writer = csv.DictWriter(f, fieldnames=headers, delimiter="\t")
            writer.writeheader()
            
            exported_ids = set()
            for td in data:
                if td[phone_key] in exported_ids:
                    continue  # Only export demographic data for each respondent once.
                exported_ids.add(td[phone_key])

                row = {
                    "phone": td[phone_key],
                    "gender": cls._get_demographic(td, gender_key),
                    "age": cls._get_demographic(td, age_key),
                    "county": cls._get_demographic(td, county_key)
                }

                if row["age"] != "NA":
                    row["age"] = cls._age_to_age_group(row["age"])

                writer.writerow(row)
