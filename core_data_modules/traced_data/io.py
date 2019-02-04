import csv
import json
import time

import jsonpickle
import pytz
from dateutil.parser import isoparse

from core_data_modules.cleaners import Codes
from core_data_modules.data_models import Label, Message
from core_data_modules.traced_data import Metadata, TracedData
from core_data_modules.util import SHAUtils

_td_type_error_string = "argument 'data' contains an element which is not of type TracedData"


class TracedDataCodaV2IO(object):
    @classmethod
    def compute_message_ids(cls, user, data, message_key, message_id_key_to_write):
        """
        Appends a message id to each object in the provided iterable of TracedData.

        Message ids are set by computing the SHA of the value at each `raw_message_key`, so are guaranteed to be stable.

        If the `raw_message_key` is not found in a TracedData object in the iterable, no message id is assigned.

        :param user: Identifier of the user running this program, for TracedData Metadata.
        :type user: str
        :param data: TracedData objects to set the message ids of.
        :type data: iterable of TracedData
        :param message_key: Key in TracedData objects of the raw text to generate message ids from.
        :type message_key: str
        :param message_id_key_to_write: Key in TracedData objects to write the message id to.
        :type message_id_key_to_write: str
        """
        for td in data:
            if message_key in td:
                td.append_data(
                    {message_id_key_to_write: SHAUtils.sha_string(td[message_key])},
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
            if td[message_id_key] in seen_message_ids:
                # This message id has been seen before, so check that the codes are the same.
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
                # This is a new message id, so add these codes to seen_message_ids
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
    def _filter_duplicates(data, message_id_key, creation_date_time_key):
        """
        Filters a list of TracedData by returning only TracedData object with each value at `message_id_key`.

        Items in data are considered duplicates if they have the same message id.
        Where duplicates are found, only the object with the oldest creation date is included in the returned list.

        :param data: Data to de-duplicate.
        :type data: iterable of TracedData
        :param message_id_key: Key in TracedData objects of the message id.
                               The returned dataset will not contain any duplicate values for this field.
        :type message_id_key: str
        :param creation_date_time_key: Key in TracedData objects of when the message was created.
                                       Where duplicates are found, the object with the oldest value here is returned.
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
        Returns whether all of the given control codes are the same and either TRUE_MISSING or SKIPPED.

        :param control_codes: Control Codes to check
        :type control_codes: iterable of str
        :return: Whether or not all of the given code_ids are the same and one of true missing, skipped, or not logical.
        :rtype: bool
        """
        if len(set(control_codes)) == 1:
            control_code = control_codes.pop()
            if control_code in {Codes.TRUE_MISSING, Codes.SKIPPED}:
                return True

        assert Codes.TRUE_MISSING not in control_codes and Codes.SKIPPED not in control_codes, \
            "Data labelled as NA or NS under one code scheme but not all of the others"

        return False

    @classmethod
    def _filter_missing(cls, data, scheme_keys):
        """
        Filters an iterable of TracedData objects to exclude those that were code as TRUE_MISSING or SKIPPED across
        all the fields in scheme_keys.

        :param data: Data to excluding objects coded as TRUE_MISSING or SKIPPED from.
        :type data: iterable of TracedData
        :param scheme_keys: Dictionary of (key in TracedData objects of coded data to export) ->
                            (Scheme for that key) :param scheme_keys:
        :type scheme_keys: dict of str -> Scheme
        :return: Data with objects coded as missing excluded.
        :rtype: iterable of TracedData
        """
        not_missing = []

        for td in data:
            control_codes = set()
            for coded_key, scheme in scheme_keys.items():
                if coded_key not in td:
                    control_codes.add(None)
                elif type(td[coded_key]) == dict:
                    control_codes.add(scheme.get_code_with_id(td[coded_key]["CodeID"]).control_code)
                else:
                    for code in td[coded_key]:
                        control_codes.add(scheme.get_code_with_id(code["CodeID"]).control_code)

            if not cls._is_coded_as_missing(control_codes):
                not_missing.append(td)

        return not_missing

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

        cls._assert_uniquely_coded(data, message_id_key, scheme_keys.keys())
        data = cls._filter_duplicates(data, message_id_key, creation_date_time_key)
        data = cls._filter_missing(data, scheme_keys)

        coda_messages = []  # List of Coda V2 Message objects to be exported
        for td in data:
            # Export labels for this row which are not Codes.NOT_CODED
            labels = []
            for coded_key, scheme in scheme_keys.items():
                if coded_key in td and scheme.get_code_with_id(td[coded_key]["CodeID"]).control_code != Codes.NOT_CODED:
                    labels.append(Label.from_firebase_map(td[coded_key]))

            # Create a Coda message object for this row
            message = Message(
                message_id=td[message_id_key],
                text=td[raw_key],
                creation_date_time_utc=isoparse(td[creation_date_time_key]).astimezone(pytz.utc).isoformat(),
                labels=labels
            )

            coda_messages.append(message)

        json.dump([m.to_firebase_map() for m in coda_messages], f, sort_keys=True, indent=2, separators=(", ", ": "))


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
