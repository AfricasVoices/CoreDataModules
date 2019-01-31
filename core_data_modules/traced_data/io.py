import time
from datetime import datetime
from os import path

import jsonpickle
import six
from dateutil.parser import isoparse

from core_data_modules.cleaners import CharacterCleaner
from core_data_modules.traced_data import Metadata, TracedData

if six.PY2:
    import unicodecsv as csv
if six.PY3:
    import csv

_td_type_error_string = "argument 'data' contains an element which is not of type TracedData"


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
