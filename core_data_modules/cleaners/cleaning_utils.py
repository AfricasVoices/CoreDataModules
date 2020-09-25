import time

from core_data_modules.cleaners import Codes
from core_data_modules.data_models import Origin, Label
from core_data_modules.traced_data import Metadata
from core_data_modules.util import TimeUtils


class CleaningUtils(object):
    @staticmethod
    def make_label_from_cleaner_code(scheme, code, origin_id, origin_name="Pipeline Auto-Coder", date_time_utc=None,
                                     set_checked=False):
        """
        Constructs a new Label object from a code determined by a pipeline cleaner.

        :param scheme: Scheme which the `code` argument belongs to.
        :type scheme: Scheme
        :param code: Code to construct the label from.
        :type code: Code
        :param origin_id: Identifier of the origin of this label.
        :type origin_id: str
        :param origin_name: Name of the origin of this label.
        :type origin_name: str
        :param date_time_utc: Date to set in the label as an ISO string in UTC, or None.
                              If None, uses the current system time in UTC.
        :type date_time_utc: str | None
        :param set_checked: Whether to set the `checked` property of the returned Label.
        :type set_checked: bool
        :return: A new label.
        :rtype: Label
        """
        if date_time_utc is None:
            date_time_utc = TimeUtils.utc_now_as_iso_string()

        origin = Origin(origin_id, origin_name, "External")

        return Label(scheme.scheme_id, code.code_id, date_time_utc, origin, checked=set_checked)

    @classmethod
    def apply_cleaner_to_traced_data_iterable(cls, user, data, raw_key, clean_key, cleaner, scheme, set_checked=False):
        """
        Applies a cleaning function to an iterable of TracedData objects, updating each with a new Label object.

        :param user: Identifier of the user running this program, for TracedData Metadata.
        :type user: str
        :param data: TracedData objects to apply the cleaner to.
        :type data: iterable of TracedData
        :param raw_key: Key in each TracedData object of the raw text to be cleaned.
        :type raw_key: str
        :param clean_key: Key in each TracedData object to write cleaned labels to.
        :type clean_key: str
        :param cleaner: Cleaning function to apply to each TracedData[`raw_key`].
        :type cleaner: function of str -> str
        :param scheme: Scheme containing codes which the strings returned from the `cleaner` can be matched against.
        :type scheme: Scheme
        :param set_checked: Whether to set the `checked` property of the applied Labels.
        :type set_checked: bool
        """
        for td in data:
            # Skip data that isn't present
            if raw_key not in td:
                continue
           
            clean_value = cleaner(td[raw_key])

            # Don't label data which the cleaners couldn't code
            if clean_value == Codes.NOT_CODED:
                continue

            # Construct a label for the clean_value returned by the cleaner
            code_id = scheme.get_code_with_match_value(clean_value)
            origin_id = Metadata.get_function_location(cleaner)
            label = cls.make_label_from_cleaner_code(scheme, code_id, origin_id, set_checked=set_checked)

            td.append_data({clean_key: label.to_dict()}, Metadata(user, Metadata.get_call_location(), time.time()))
