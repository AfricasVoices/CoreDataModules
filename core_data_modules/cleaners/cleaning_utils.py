import time
from datetime import datetime

import pytz

from core_data_modules.cleaners import Codes
from core_data_modules.data_models import Origin, Label
from core_data_modules.traced_data import Metadata


class CleaningUtils(object):
    @staticmethod
    def make_label(scheme, code, origin_id, origin_name="Pipeline Auto-Coder", date_time_utc=None):
        if date_time_utc is None:
            date_time_utc = datetime.now().astimezone(pytz.utc).isoformat()

        origin = Origin(origin_id, origin_name, "External")

        return Label(scheme.scheme_id, code.cod_id, date_time_utc, origin, checked=False)

    @classmethod
    def apply_cleaner_to_traced_data_iterable(cls, user, data, raw_key, clean_key, cleaner, scheme):
        for td in data:
            # Don't clean missing data
            if td.get(clean_key) is not None and \
                    scheme.get_code_with_id(td[clean_key]["CodeID"]).control_code in {Codes.TRUE_MISSING, Codes.SKIPPED}:
                continue

            code = cleaner(td[raw_key])

            # Don't code data which the cleaners couldn't code
            # TODO: Update the cleaners to return something other than Codes.NOT_CODED
            if code == Codes.NOT_CODED:
                continue

            code_id = scheme.get_code_with_match_value(code)
            origin_id = Metadata.get_function_location(cleaner)
            label = cls.make_label(scheme, code_id, origin_id)

            td.append_data({clean_key: label.to_dict()}, Metadata(user, Metadata.get_call_location(), time.time()))
