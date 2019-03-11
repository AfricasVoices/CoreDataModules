import csv
import io
import json
import time

import jsonpickle
import pytz
from dateutil.parser import isoparse

from core_data_modules.cleaners import Codes
from core_data_modules.cleaners.cleaning_utils import CleaningUtils
from core_data_modules.data_models import Label, Message
from core_data_modules.traced_data import Metadata, TracedData
from core_data_modules.util import SHAUtils, TimeUtils

_td_type_error_string = "argument 'data' contains an element which is not of type TracedData"


class TracedDataCodaV2IO(object):
    @classmethod
    def compute_message_ids(cls, user, data, message_key, message_id_key_to_write):
        """
        Appends a message id to each object in the provided iterable of TracedData.

        Message ids are set by computing the SHA of the value at each `message_key`, so are guaranteed to be stable.

        If the `message_key` is not found in a TracedData object in the iterable, no message id is assigned.

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

    @classmethod
    def export_traced_data_iterable_to_coda_2(cls, data, raw_key, creation_date_time_key, message_id_key,
                                              scheme_key_map, f):
        """
        Exports an iterable of TracedData to a messages json file suitable for upload into Coda V2.

        Data is de-duplicated on export.

        TracedData objects which do not contain the given raw_key, or which the value at raw_key is empty string,
        will not have data exported.
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
        :param scheme_key_map: Dictionary of (key in TracedData objects of coded data to export) ->
                               (Scheme for that key)
        :type scheme_key_map: dict of str -> Scheme
        :param f: File to write exported JSON file to.
        :type f: file-like
        """
        # Filter data for elements which contain a value for the given raw key that isn't empty string
        filtered_data = [td for td in data if td.get(raw_key, "") != ""]

        cls._assert_uniquely_coded(filtered_data, message_id_key, scheme_key_map.keys())
        filtered_data = cls._filter_duplicates(filtered_data, message_id_key, creation_date_time_key)

        coda_messages = []  # List of Coda V2 Message objects to be exported
        for td in filtered_data:
            # Export labels for this row which are not Codes.NOT_CODED
            labels = []
            for coded_key, scheme in scheme_key_map.items():
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

    @staticmethod
    def _make_empty_file():
        """
        :return: Object which looks like a Coda 2 messages file containing no messages.
        :rtype: StringIO
        """
        return io.StringIO("[]")

    @staticmethod
    def _dataset_lut_from_messages_file(f, schemes_to_parse):
        """
        Creates a lookup table of MessageID -> SchemeID -> Labels from the given Coda 2 messages file.
        
        Labels from schemes which are duplicates are automatically placed in the look-up table for the primary scheme.

        :param f: Coda 2 messages file.
        :type f: file-like
        :param schemes_to_parse: Primary schemes to include in the returned LUT.
        :type schemes_to_parse: iterable of Scheme
        :return: Lookup table.
        :rtype: dict of str -> (dict of str -> list of Label)
        """
        assert f.tell() == 0, "File-pointer not at byte 0. " \
                              "Should you have used e.g. `f.seek(0)` before calling this method?"

        coda_messages_file = json.load(f)
        messages = []
        for json_msg in coda_messages_file:
            messages.append(Message.from_firebase_map(json_msg))

        dataset_lut = dict()  # of MessageID -> (dict of SchemeID -> list of Label)
        for msg in messages:
            schemes_lut = dict()  # of SchemeID -> list of Label (for this message)
            dataset_lut[msg.message_id] = schemes_lut

            for label in msg.labels:
                for scheme_to_parse in schemes_to_parse:
                    if label.scheme_id == scheme_to_parse.scheme_id or label.scheme_id.startswith(scheme_to_parse.scheme_id):
                        primary_scheme_id = scheme_to_parse.scheme_id
                        if primary_scheme_id not in schemes_lut:
                            schemes_lut[primary_scheme_id] = []
                        schemes_lut[primary_scheme_id].append(label)

        return dataset_lut

    @classmethod
    def import_coda_2_to_traced_data_iterable(cls, user, data, message_id_key, scheme_key_map, f=None):
        """
        Codes keys in an iterable of TracedData objects by using the codes from a Coda 2 messages JSON file.

        Data which is has not been checked in the Coda file is coded using the provided nr_label
        (irrespective of whether there was an automatic code there before).

        TODO: Data which has been assigned a code under one scheme but none of the others needs to coded as NC not NR
        TODO: Or, do this in Coda so as to remove ambiguity from the perspective of the RAs?

        :param user: Identifier of user running this program.
        :type user: str
        :param data: TracedData objects to be coded using the Coda file.
        :type data: iterable of TracedData
        :param message_id_key: Key in TracedData objects of the message ids.
        :type message_id_key: str
        :param scheme_key_map: Dictionary of (key in TracedData objects to assign labels to) ->
                               (Scheme in the Coda messages file to retrieve the labels from)
        :type scheme_key_map: dict of str -> Scheme
        :param f: Coda data file to import codes from, or None.
        :type f: file-like | None
        """
        if f is None:
            f = cls._make_empty_file()

        # Build a lookup table of MessageID -> SchemeID -> Labels
        coda_dataset = cls._dataset_lut_from_messages_file(f, scheme_key_map.values())

        # Filter out TracedData objects that do not contain a message id key
        data = [td for td in data if message_id_key in td]

        # Apply the labels from Coda to each TracedData item in data
        for td in data:
            for key_of_coded, scheme in scheme_key_map.items():
                # Get labels for this (message id, scheme id) from the look-up table
                labels = coda_dataset.get(td[message_id_key], dict()).get(scheme.scheme_id, [])
                if labels is not None:
                    # Append each label that was assigned to this message for this scheme to the TracedData.
                    for label in reversed(labels):
                        td.append_data({key_of_coded: label.to_dict()},
                                       Metadata(user, Metadata.get_call_location(), TimeUtils.utc_now_as_iso_string()))

                # If this td still has no label after importing from the Coda file, or the label is a non-missing label
                # that hasn't been checked in the Coda UI, set a code for NOT_REVIEWED
                if key_of_coded not in td or not td[key_of_coded]["Checked"]:
                    nr_label = CleaningUtils.make_label_from_cleaner_code(
                        scheme, scheme.get_code_with_control_code(Codes.NOT_REVIEWED),
                        Metadata.get_call_location()
                    )
                    td.append_data(
                        {key_of_coded: nr_label.to_dict()},
                        Metadata(user, Metadata.get_call_location(), time.time())
                    )

    @classmethod
    def import_coda_2_to_traced_data_iterable_multi_coded(cls, user, data, message_id_key, scheme_key_map, f=None):
        """
        Codes keys in an iterable of TracedData objects by using the codes from a Coda 2 messages JSON file.

        Data which is has not been checked in the Coda file is coded using the provided nr_label
        (irrespective of whether there was an automatic code there before).
        
        Only the 'primary' schemes should be passed in. Schemes that have been duplicated using the duplicate_scheme
        tool in CodaV2/data_tools will be detected as being associated with the primary scheme automatically.

        TODO: Data which has been assigned a code under one scheme but none of the others needs to coded as NC not NR
        TODO: Or, do this in Coda so as to remove ambiguity from the perspective of the RAs?

        :param user: Identifier of user running this program.
        :type user: str
        :param data: TracedData objects to be coded using the Coda file.
        :type data: iterable of TracedData
        :param message_id_key: Key in TracedData objects of the message ids.
        :type message_id_key: str
        :param scheme_key_map: Dictionary of (key in TracedData objects to assign labels to) ->
                            (Scheme in the Coda messages file to retrieve the labels from)
        :type scheme_key_map: dict of str -> iterable of Scheme
        :param f: Coda data file to import codes from, or None. If None, assigns NOT_REVIEWED codes to everything.
        :type f: file-like | None
        """
        if f is None:
            f = cls._make_empty_file()

        # Build a lookup table of MessageID -> SchemeID -> Labels
        coda_dataset = cls._dataset_lut_from_messages_file(f, scheme_key_map.values())

        # Filter out TracedData objects that do not contain a message id key
        data = [td for td in data if message_id_key in td]

        # Apply the labels from Coda to each TracedData item in data
        for td in data:
            for coded_key, scheme in scheme_key_map.items():
                # Get labels for this (message id, scheme id) from the look-up table
                labels = coda_dataset.get(td[message_id_key], dict()).get(scheme.scheme_id, [])

                # Get the currently assigned list of labels for this multi-coded scheme,
                # and construct a look-up table of scheme id -> label
                td_labels = td.get(coded_key, [])
                td_labels_lut = {label["SchemeID"]: Label.from_dict(label) for label in td_labels}

                for label in reversed(labels):
                    # Update the relevant label in this traced data's list of labels with the new label,
                    # and append the whole new list to the traced data.
                    td_labels_lut[label.scheme_id] = label

                    td_labels = list(td_labels_lut.values())
                    td.append_data({coded_key: [label.to_dict() for label in td_labels]},
                                   Metadata(user, Metadata.get_call_location(), TimeUtils.utc_now_as_iso_string()))

                # Delete any labels that are SPECIAL-MANUALLY_UNCODED
                for scheme_id, label in list(td_labels_lut.items()):
                    if label.code_id == "SPECIAL-MANUALLY_UNCODED":
                        del td_labels_lut[scheme_id]
                        td_labels = list(td_labels_lut.values())
                        td.append_data({coded_key: [label.to_dict() for label in td_labels]},
                                       Metadata(user, Metadata.get_call_location(), time.time()))

                # If no manual labels have been set and are checked, set a code for NOT_REVIEWED
                checked_codes_count = 0
                labels = td.get(coded_key)
                if labels is not None:
                    for label in labels:
                        if label["Checked"]:
                            checked_codes_count += 1

                if checked_codes_count == 0:
                    nr_label = CleaningUtils.make_label_from_cleaner_code(
                        scheme, scheme.get_code_with_control_code(Codes.NOT_REVIEWED),
                        Metadata.get_call_location()
                    )

                    td.append_data(
                        {coded_key: [nr_label.to_dict()]},
                        Metadata(user, Metadata.get_call_location(), time.time())
                    )


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
                for key in td:
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
