import json
import time
from datetime import datetime
from os import path

import jsonpickle
import pytz as pytz
import six
from dateutil.parser import isoparse

from core_data_modules.cleaners import CharacterCleaner, Codes
from core_data_modules.data_models import Message, Label
from core_data_modules.traced_data import Metadata, TracedData
from core_data_modules.util import SHAUtils

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
    def exclude_missing(data, key_of_raw):
        """
        Filters a collection of TracedData objects to remove those where the value for 'key_of_raw' is 
        Codes.TRUE_MISSING, Codes.SKIPPED, or Codes.NOT_INTERNALLY_CONSISTENT.

        :param data: TracedData objects to filter.
        :type data: iterable of TracedData
        :param key_of_raw: Key in TracedData objects of raw messages to filter on.
        :type key_of_raw: str
        :return: Filtered TracedData objects.
        :rtype: iterable of TracedData
        """
        return [td for td in data
                if td[key_of_raw] not in {Codes.TRUE_MISSING, Codes.SKIPPED, Codes.NOT_INTERNALLY_CONSISTENT}]

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
        return [td for td in data if td.get(key, Codes.NOT_CODED) in {Codes.NOT_CODED, Codes.NOT_REVIEWED}]


class TracedDataCodaIO(object):
    coda_data_col = "data"
    coda_scheme_name_col = "schemeName"
    coda_code_value_col = "deco_codeValue"

    overwritable_codes = {Codes.NOT_CODED, Codes.NOT_REVIEWED}  # Codes which may always be overwritten on import

    @staticmethod
    def _generate_new_coda_id(existing_ids):
        for i in range(1, 1000):
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
        
        Missing data (Codes.TRUE_MISSING, .SKIPPED, and .NOT_INTERNALLY_CONSISTENT) are not exported to Coda.

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

        # Filter out TracedData objects with missing data for this column
        not_missing_data = _TracedDataIOUtil.exclude_missing(data, key_of_raw)

        # De-duplicate raw messages
        unique_data = _TracedDataIOUtil.unique_messages(not_missing_data, key_of_raw)

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

        Missing data (Codes.TRUE_MISSING, .SKIPPED, and .NOT_INTERNALLY_CONSISTENT) are not exported to Coda.

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

        # Filter out TracedData objects with missing data for this column
        not_missing_data = _TracedDataIOUtil.exclude_missing(data, key_of_raw)

        # De-duplicate raw messages
        unique_data = _TracedDataIOUtil.unique_messages(not_missing_data, key_of_raw)

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
                    assert scheme_code_ids[prev_code_value] == row["deco_codeId"], \
                        "Error: Code value '{}' has conflicting scheme ids (observed ids '{}' and " \
                        "'{}')".format(prev_code_value, scheme_code_ids[prev_code_value], row["deco_codeId"])

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
                        new_code_id = cls._generate_new_coda_id(
                            [int(id.split("-")[1]) for id in scheme_code_ids.values()])
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

    @classmethod
    def import_coda_to_traced_data_iterable(cls, user, data, key_of_raw, scheme_keys, f,
                                            overwrite_existing_codes=False):
        """
        Codes a "column" of a collection of TracedData objects by using the codes from a Coda data-file.

        Raw values which are Codes.TRUE_MISSING, Codes.SKIPPED, or Codes.NOT_INTERNALLY_CONSISTENT are copied through
        to the coded keys. Data which is has not been assigned a code in the Coda file is coded as Codes.NOT_REVIEWED.

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

        # Build a lookup table of (raw_data, scheme_name) -> row containing only the rows which have been coded.
        coded = {(row[cls.coda_data_col], row[cls.coda_scheme_name_col]): row
                 for row in imported_csv if row[cls.coda_code_value_col] != ""}

        for td in data:
            for scheme_name, key_of_coded in scheme_keys.items():
                if not overwrite_existing_codes and td.get(key_of_coded, Codes.NOT_CODED) not in cls.overwritable_codes:
                    continue

                coded_lookup_key = (td[key_of_raw], scheme_name)
                if td[key_of_raw] in {Codes.TRUE_MISSING, Codes.SKIPPED, Codes.NOT_INTERNALLY_CONSISTENT}:
                    code = td[key_of_raw]
                elif coded_lookup_key in coded:
                    code = coded[coded_lookup_key][cls.coda_code_value_col]
                else:
                    code = Codes.NOT_REVIEWED

                td.append_data({key_of_coded: code}, Metadata(user, Metadata.get_call_location(), time.time()))

    @classmethod
    def import_coda_to_traced_data_iterable_as_matrix(cls, user, data, key_of_raw, coda_keys, f,
                                                      key_of_coded_prefix=""):
        # TODO: Add option for not overwriting existing codes? This exists in import_coda_to_traced_data_iterable,
        # TODO: but has always been set to True.
        """
        Codes a collection of TracedData objects by interpreting the specified schemes in a Coda file as
        multiple-select answers.

        Coda data is imported by adding a key in each TracedData object for each of the code values observed in the
        specified `coda_keys`, and setting the value of each added key to either Codes.MATRIX_1 or Codes.MATRIX_0
        depending on whether or not that code exists on that message.

        For example, a Coda file with the coda_keys "reason 1" and "reason 2", which collectively contain the options
        "water", "food", and "clothes", will append the keys "water", "food", and "clothes" to each TracedData item,
        each set to Codes.MATRIX_1 if that value was present in "reason 1" or in "reason 2" for that TracedData item's
        raw data; Codes.MATRIX_0 otherwise.

        Data which is has not been assigned a code in the Coda file will have <key_of_coded_prefix>NR set to
        Codes.MATRIX_1.

        :param user: Identifier of user running this program
        :type user: str
        :param data: TracedData objects to be coded using the Coda file.
        :type data: iterable of TracedData
        :param key_of_raw: Key in the TracedData objects of messages which should be coded.
        :type key_of_raw: str
        :param coda_keys: Names of the code schemes in the Coda file to import.
        :type coda_keys: iterable of str
        :param f: Coda data file to import codes from.
        :type f: file-like
        :param key_of_coded_prefix: String to prefix keys appended to each TracedData object with.
        :type key_of_coded_prefix: str
        """
        imported_csv = csv.DictReader(f, delimiter=";")

        # Remove rows which still haven't been coded.
        coded = [row for row in imported_csv if row[cls.coda_code_value_col] != ""]

        # Determine the available matrix headings from examination of all the code values which have been set
        # across all the specified coda keys.
        all_matrix_keys = {row[cls.coda_code_value_col] for row in coded if row[cls.coda_scheme_name_col] in coda_keys}
        all_matrix_keys.add(Codes.NOT_REVIEWED)

        # Find codes assigned to each row of the coded data
        coded_matrix_keys = dict()  # of message -> set of codes assigned
        for row in coded:
            # Skip schemes not in code_keys
            if row[cls.coda_scheme_name_col] not in coda_keys:
                continue

            message = row[cls.coda_data_col]
            if message not in coded_matrix_keys:
                coded_matrix_keys[message] = set()
            coded_matrix_keys[message].add(row[cls.coda_code_value_col])

        # Apply the codes to each td in data
        for td in data:
            # Determine which matrix keys have been set for this TracedData item,
            # by using the dictionary coded_matrix_keys as set above if this message was found in the Coda file,
            # otherwise by using Codes.NOT_REVIEWED
            td_matrix_keys = coded_matrix_keys.get(td[key_of_raw], {Codes.NOT_REVIEWED})

            # Construct and set the matrix for this TracedData item accordingly.
            td_matrix_data = dict()
            for matrix_key in all_matrix_keys:
                output_key = "{}{}".format(key_of_coded_prefix, matrix_key)
                td_matrix_data[output_key] = Codes.MATRIX_1 if matrix_key in td_matrix_keys else Codes.MATRIX_0

            td.append_data(td_matrix_data, Metadata(user, Metadata.get_call_location(), time.time()))


class TracedDataCoda2IO(object):
    @classmethod
    def add_message_ids(cls, user, data, raw_key, message_id_key):
        """
        Appends a message id to each object in the provided iterable of TracedData.
        
        Message ids are set by computing the SHA of the value at each `raw_key`, so are guaranteed to be stable.

        If the `raw_key` is not found in a TracedData object in the iterable, no message id is assigned.
        
        :param user: Identifier of the user running this program, for TracedData Metadata.
        :type user: str
        :param data: TracedData objects to set message_ids for.
        :type data: iterable of TracedData
        :param raw_key: Key in TracedData objects to read the text to generate message ids for from.
        :type raw_key: str
        :param message_id_key: Key in TracedData objects to write the message id to.
        :type message_id_key: str
        """
        for td in data:
            if raw_key in td:
                td.append_data(
                    {message_id_key: SHAUtils.sha_string(td[raw_key])},
                    Metadata(user, Metadata.get_call_location(), time.time())
                )

    @staticmethod
    def _assert_uniquely_coded(data, message_id_key, coded_keys):
        """
        Checks that all objects with the same message id have been assigned the same codes for each coded_key in
        coded_keys.

        Fails with an AssertionError if there are TracedData objects with the same message id but different codes 
        assigned, otherwise has no side-effects.

        :param data: Data to check.
        :type data: iterable of TracedData
        :param message_id_key: Key in TracedData objects of the message id.
        :type message_id_key: str
        :param coded_keys: Keys in the TracedData objects containing coded data.
        :type coded_keys: iterable of str
        """
        seen_message_ids = dict()  # of message_id -> coded_key -> set of code_ids
        for td in data:
            # If this message id has been seen before, check that the codes are the same,
            # otherwise add these codes to seen_code_ids for future tests
            if td[message_id_key] in seen_message_ids:
                seen_code_ids = seen_message_ids[td[message_id_key]]
                for coded_key in coded_keys:
                    err_string = "Messages with the same id ({}) have different " \
                                 "labels for coded_key '{}'".format(td[message_id_key], coded_key)

                    if coded_key not in td:
                        assert seen_code_ids[coded_key] is None, err_string
                    elif type(td[coded_key]) == dict:
                        assert seen_code_ids[coded_key] == td[coded_key]["CodeID"], err_string
                    else:
                        assert seen_code_ids[coded_key] == {label["CodeID"] for label in td[coded_key]}, err_string
            else:
                new_code_ids = dict()
                for coded_key in coded_keys:
                    if coded_key not in td:
                        new_code_ids[coded_key] = None
                    elif type(td[coded_key]) == dict:
                        new_code_ids[coded_key] = td[coded_key]["CodeID"]
                    else:
                        new_code_ids[coded_key] = {label["CodeID"] for label in td[coded_key]}
                seen_message_ids[td[message_id_key]] = new_code_ids

    @staticmethod
    def _de_duplicate_data(data, message_id_key, creation_date_time_key):
        """
        De-duplicates data.
        
        Items in data are considered duplicates if they have the same message id.
        Where duplicates are found, the object with the oldest creation date is returned
        
        :param data: Data to de-duplicate.
        :type data: iterable of TracedData
        :param message_id_key: Key in TracedData objects of the message id.
                               The returned dataset will not contain any duplicate values for this field.
        :type message_id_key: str
        :param creation_date_time_key: Key in TracedData objects of when the message was created.
                                       Where duplicates are found, the object with the oldest value here is returned.s
        :type creation_date_time_key: str
        :return: De-duplicated TracedData objects.
        :rtype: list of TracedData
        """
        # Sort data oldest first in order to set the CreationDateTimeUTC keys correctly
        data.sort(key=lambda td: isoparse(td[creation_date_time_key]))

        seen_ids = set()
        unique_data = []
        for td in data:
            if td[message_id_key] not in seen_ids:
                seen_ids.add(td[message_id_key])
                unique_data.append(td)

        return unique_data

    @staticmethod
    def _is_coded_as_missing(control_codes):
        """
        Returns whether all of the given control codes are the same and either TRUE_MISSING or SKIPPED

        :param control_codes: Control Codes to check
        :type control_codes: iterable of str
        :return: Whether or not all of the given code_ids are the same and one of true missing, skipped, or not logical.
        :rtype: bool
        """
        # TODO: The logic here needs to change.
        #       Probably to something like if NA or NS in the set of control codes, assert that all
        #       codes are the same then return True. This probably isn't actually strong enough either -
        #       we need to make sure there are no non-missing labels assigned to any of the schemes being exported.

        if len(set(control_codes)) == 1:
            control_code = control_codes.pop()
            if control_code in {Codes.TRUE_MISSING, Codes.SKIPPED}:
                return True
        return False

    @classmethod
    def export_traced_data_iterable_to_coda_2(cls, data, raw_key, creation_date_time_key, message_id_key,
                                              scheme_keys, f):
        """
        Exports an iterable of TracedData to a messages json file suitable for upload into Coda V2.

        Data is de-duplicated on export.

        TracedData objects which do not contain the given raw_key will not have data exported.
        Data which has been coded as TRUE_MISSING or SKIPPED will not be exported.
        Data which has been coded as NOT_CODED will be exported but without the NOT_CODED label.
        TracedData objects with the same message id must have the same labels applied, otherwise this exporter will fail.

        :param data: Data to export to Coda V2.
        :type data: iterable of TracedData
        :param raw_key: Key in TracedData objects of the raw messages.
        :type raw_key: str
        :param creation_date_time_key: Key in TracedData objects of when the message was created.
        :type creation_date_time_key: str
        :param message_id_key: Key in TracedData objects of the message id.
                               Message Ids may be set using TracedDataCoda2IO.add_message_ids.
        :type message_id_key: str
        :param scheme_keys: Dictionary of (key in TracedData objects of coded data to export) ->
                            (Scheme for that key)
        :type scheme_keys: dict of str -> Scheme
        :param f: File to write exported JSON file to.
        :type f: file-like
        """
        # Filter data for elements which contain the given raw key
        data = [td for td in data if raw_key in td]

        # Assert uniquely coded
        cls._assert_uniquely_coded(data, message_id_key, scheme_keys.keys())

        # De-duplicate
        data = cls._de_duplicate_data(data, message_id_key, creation_date_time_key)

        coda_messages = []  # List of Coda V2 Message objects to be exported
        for td in data:
            # Skip messages which have been coded as missing across all scheme_keys
            control_codes = []
            for coded_key, scheme in scheme_keys.items():
                if coded_key not in td:
                    continue

                if type(td[coded_key]) == dict:
                    control_codes.append(scheme.get_code_with_id(td[coded_key]["CodeID"]).control_code)
                else:
                    for code in td[coded_key]:
                        control_codes.append(scheme.get_code_with_id(code["CodeID"]).control_code)
            if cls._is_coded_as_missing(control_codes):
                continue

            # Create a Coda message object for this row
            message = Message(
                message_id=td[message_id_key],
                text=td[raw_key],
                creation_date_time_utc=isoparse(td[creation_date_time_key]).astimezone(pytz.utc).isoformat(),
                labels=[]
            )

            # Export codes for this row which are not Codes.NOT_CODED
            for coded_key, scheme in scheme_keys.items():
                if coded_key in td and scheme.get_code_with_id(td[coded_key]["CodeID"]).control_code != Codes.NOT_CODED:
                    message.labels.append(Label.from_firebase_map(td[coded_key]))

            coda_messages.append(message)

        json.dump([m.to_firebase_map() for m in coda_messages], f, sort_keys=True, indent=2, separators=(", ", ": "))

    @staticmethod
    def _dataset_lut_from_messages_file(f):
        """
        Creates a lookup table of MessageID -> SchemeID -> Labels from the given Coda 2 messages file.

        :param f: Coda 2 messages file.
        :type f: file-like
        :return: Lookup table.
        :rtype: dict of str -> (dict of str -> list of dict)
        """
        coda_dataset = dict()  # of MessageID -> (dict of SchemeID -> list of Label)

        for msg in json.load(f):
            schemes = dict()  # of SchemeID -> list of Label
            coda_dataset[msg["MessageID"]] = schemes
            msg["Labels"].reverse()
            for label in msg["Labels"]:
                scheme_id = label["SchemeID"]
                if scheme_id not in schemes:
                    schemes[scheme_id] = []
                schemes[scheme_id].append(label)

        return coda_dataset

    @classmethod
    def import_coda_2_to_traced_data_iterable(cls, user, data, message_id_key, scheme_keys, nr_label, f):
        """
        Codes keys in an iterable of TracedData objects by using the codes from a Coda 2 messages JSON file.

        Data which is has not been checked in the Coda file is coded using the provided nr_label
        (irrespective of whether there was an automatic code there before).
        Data which was previously coded as TRUE_MISSING or SKIPPED is untouched, irrespective of how that code
        was assigned.

        TODO: Data which has been assigned a code under one scheme but none of the others needs to coded as NC not NR
        TODO: Or, do this in Coda so as to remove ambiguity from the perspective of the RAs?

        :param user: Identifier of user running this program.
        :type user: str
        :param data: TracedData objects to be coded using the Coda file.
        :type data: iterable of TracedData
        :param message_id_key: Key in TracedData objects of the message ids.
        :type message_id_key: str
        :param scheme_keys: Dictionary of (key in TracedData objects to assign labels to) ->
                            (Schemes in the Coda messages file to retrieve the labels from)
        :type scheme_keys: dict of str -> Scheme
        :param nr_label: Label to apply to messages which haven't been reviewed yet.
        :type nr_label: core_data_modules.data_models.Label
        :param f: Coda data file to import codes from.
        :type f: file-like
        """
        # Build a lookup table of MessageID -> SchemeID -> Labels
        coda_dataset = cls._dataset_lut_from_messages_file(f)

        # Apply the labels from Coda to each TracedData item in data
        for td in data:
            if message_id_key not in td:
                continue

            for key_of_coded, scheme in scheme_keys.items():
                labels = coda_dataset.get(td[message_id_key], dict()).get(scheme.scheme_id)
                if labels is not None:
                    for label in labels:
                        # TODO: Check not duplicating previous history?
                        td.append_data(
                            {key_of_coded: label},
                            Metadata(user, Metadata.get_call_location(),
                                     (isoparse(label["DateTimeUTC"]) - datetime(1970, 1, 1,
                                                                                tzinfo=pytz.utc)).total_seconds())
                        )

                    if key_of_coded not in td or not td[key_of_coded]["Checked"] or \
                            td[key_of_coded]["CodeID"] == "SPECIAL-MANUALLY_UNCODED":
                        td.append_data(
                            {key_of_coded: nr_label.to_dict()},
                            Metadata(user, Metadata.get_call_location(), time.time())
                        )
                elif key_of_coded not in td or \
                        not cls._is_coded_as_missing([scheme.get_code_with_id(td[key_of_coded]["CodeID"]).control_code]):
                    td.append_data(
                        {key_of_coded: nr_label.to_dict()},
                        Metadata(user, Metadata.get_call_location(), time.time())
                    )

    @classmethod
    def import_coda_2_to_traced_data_iterable_multi_coded(cls, user, data, message_id_key, scheme_keys,
                                                          nr_label, f):
        """
        Codes keys in an iterable of TracedData objects by using the codes from a Coda 2 messages JSON file.

        Data which is has not been checked in the Coda file is coded using the provided nr_label
        (irrespective of whether there was an automatic code there before).
        Data which was previously coded as TRUE_MISSING, SKIPPED, or NOT_LOGICAL by any means is untouched.

        TODO: Data which has been assigned a code under one scheme but none of the others needs to coded as NC not NR
        TODO: Or, do this in Coda so as to remove ambiguity from the perspective of the RAs?

        :param user: Identifier of user running this program.
        :type user: str
        :param data: TracedData objects to be coded using the Coda file.
        :type data: iterable of TracedData
        :param message_id_key: Key in TracedData objects of the message ids.
        :type message_id_key: str
        :param scheme_keys: Dictionary of (key in TracedData objects to assign labels to) ->
                            (Schemes in the Coda messages file to retrieve the labels from)
        :type scheme_keys: dict of str -> list of Scheme
        :param nr_label: Label to apply to messages which haven't been reviewed yet.
        :type nr_label: core_data_modules.data_models.Label
        :type scheme_keys: dict of str -> list of str
        :param f: Coda data file to import codes from.
        :type f: file-like
        """
        # Build a lookup table of MessageID -> SchemeID -> Labels
        coda_dataset = cls._dataset_lut_from_messages_file(f)

        # Assert that all the groups of scheme items have the same codes (i.e. they all duplicates)
        for schemes in scheme_keys.values():
            head_scheme = list(schemes)[0]
            for scheme in schemes:
                assert scheme.codes == head_scheme.codes

        # Apply the labels from Coda to each TracedData item in data
        for td in data:
            if message_id_key not in td:
                continue

            for coded_key, schemes in scheme_keys.items():
                scheme = list(schemes)[0]

                # Get all the labels assigned to this scheme across all the virtual schemes in Coda,
                # and sort oldest first.
                labels = []
                for scheme in scheme_keys[coded_key]:
                    labels.extend(coda_dataset.get(td[message_id_key], dict()).get(scheme.scheme_id, []))
                labels.sort(key=lambda l: isoparse(l["DateTimeUTC"]))

                # Get the currently assigned list of codes for this multi-coded scheme
                td_codes = td.get(coded_key, [])
                td_codes_lut = {code["SchemeID"]: code for code in td_codes}

                for label in labels:
                    # Update the relevant label in this traced data's list of labels with the new label,
                    # and append the whole new list to the traced data.
                    td_codes_lut[label["SchemeID"]] = label

                    if len(td_codes_lut) > 1:
                        for key, code in td_codes_lut.items():
                            if scheme.get_code_with_id(code["CodeID"]).control_code == Codes.NOT_CODED:
                                del td_codes_lut[key]

                    td_codes = list(td_codes_lut.values())
                    td.append_data({coded_key: td_codes},
                                   Metadata(user, Metadata.get_call_location(),
                                            (isoparse(label["DateTimeUTC"]) - datetime(1970, 1, 1,
                                                                                       tzinfo=pytz.utc)).total_seconds()))

                for scheme_id, code in list(td_codes_lut.items()):
                    if code["CodeID"] == "SPECIAL-MANUALLY_UNCODED":
                        del td_codes_lut[scheme_id]
                        td_codes = list(td_codes_lut.values())
                        td.append_data({coded_key: td_codes}, Metadata(user, Metadata.get_call_location(), time.time()))

                checked_codes_count = 0
                coded_as_missing = False
                labels = td.get(coded_key)
                if labels is not None:
                    for label in labels:
                        if label["Checked"]:
                            checked_codes_count += 1
                    coded_as_missing = cls._is_coded_as_missing(
                        [scheme.get_code_with_id(label["CodeID"]).control_code for label in labels])

                if checked_codes_count == 0 and not coded_as_missing:
                    td.append_data(
                        {coded_key: [nr_label.to_dict()]},
                        Metadata(user, Metadata.get_call_location(), time.time())
                    )


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
                    row["message"] = u"{} {}".format(message_key, row["message"])

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
