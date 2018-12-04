import time
from datetime import datetime

import pytz

from core_data_modules.cleaners import Codes
from core_data_modules.data_models import Origin, Label
from core_data_modules.traced_data import Metadata


class CleaningUtils(object):
    @staticmethod
    def make_cleaner_label(scheme, code, origin_id, origin_name="Pipeline Auto-Coder", date_time_utc=None):
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
        :return: A new label.
        :rtype: Label
        """
        if date_time_utc is None:
            date_time_utc = datetime.now().astimezone(pytz.utc).isoformat()

        origin = Origin(origin_id, origin_name, "External")

        return Label(scheme.scheme_id, code.code_id, date_time_utc, origin, checked=False)

    @classmethod
    def apply_cleaner_to_traced_data_iterable(cls, user, data, raw_key, clean_key, cleaner, scheme):
        """
        Applies a cleaning function to an iterable of TracedData objects, updating each with a new Label object.

        TracedData objects which have already been coded as TRUE_MISSING or SKIPPED in `clean_key` are not cleaned.
        
        :param user: Identifier of the user running this program, for TracedData Metadata.
        :type user: str
        :param data: TracedData objects to apply the cleaner to.
        :type data: iterable of TracedData
        :param raw_key: Key in each TracedData object of the raw text to be cleaned.
        :type raw_key: str
        :param clean_key: Key in each TracedData object to write cleaned labels to.
                          These keys may already be present in TracedData objects. In such cases:
                           - Keys which have been labelled as TRUE_MISSING or SKIPPED under this scheme are
                             left untouched.
                           - All other keys are overwritten with new codes.
        :type clean_key: str
        :param cleaner: Cleaning function to apply to each TracedData[`raw_key`].
        :type cleaner: function of str -> str
        :param scheme: Scheme containing codes which the strings returned from the `cleaner` can be matched against.
        :type scheme: Scheme
        """
        for td in data:
            # Don't re-clean data which has already been coded as missing
            if td.get(clean_key) is not None and \
                    scheme.get_code_with_id(td[clean_key]["CodeID"]).control_code in {Codes.TRUE_MISSING, Codes.SKIPPED}:
                continue

            clean_value = cleaner(td[raw_key])

            # Don't label data which the cleaners couldn't code
            if clean_value == Codes.NOT_CODED:
                continue

            # Construct a label for the clean_value returned by the cleaner
            code_id = scheme.get_code_with_match_value(clean_value)
            origin_id = Metadata.get_function_location(cleaner)
            label = cls.make_cleaner_label(scheme, code_id, origin_id)

            td.append_data({clean_key: label.to_dict()}, Metadata(user, Metadata.get_call_location(), time.time()))
