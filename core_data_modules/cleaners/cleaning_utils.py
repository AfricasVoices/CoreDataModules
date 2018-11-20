import time
from datetime import datetime

import pytz

from core_data_modules.cleaners import Codes
from core_data_modules.data_models import Origin, Label
from core_data_modules.traced_data import Metadata


class CleaningUtils(object):
    @staticmethod
    def make_label(scheme_id, code_id, origin_id, origin_name="Pipeline Auto-Coder",
                   date_time_utc=None, control_code=None):
        if date_time_utc is None:
            date_time_utc = datetime.now().astimezone(pytz.utc).isoformat()

        label = Label()
        label.scheme_id = scheme_id
        label.code_id = code_id
        label.date_time_utc = date_time_utc
        label.checked = False
        label.confidence = 0  # TODO
        # Skipping label_set for now
        if control_code is None:
            label.code_type = "Normal"
        else:
            label.control_code = control_code
            label.code_type = "Control"

        origin = Origin()
        origin.origin_id = origin_id
        origin.name = origin_name
        origin.origin_type = "External"
        label.origin = origin

        return label

    @classmethod
    def apply_cleaner_to_traced_data_iterable(cls, user, data, raw_key, clean_key, cleaner, code_translator):
        for td in data:
            # Don't clean missing data
            if td.get(clean_key) is not None and \
                    td[clean_key].get("ControlCode") in {Codes.TRUE_MISSING, Codes.SKIPPED, Codes.NOT_LOGICAL}:
                continue

            code = cleaner(td[raw_key])
            control_code = Codes.NOT_CODED if code == Codes.NOT_CODED else None
            code_id = code_translator.code_id(code)
            origin_id = Metadata.get_function_location(cleaner)
            label = cls.make_label(code_translator.scheme_id, code_id, origin_id, control_code=control_code)

            td.append_data({clean_key: label.to_dict()}, Metadata(user, Metadata.get_call_location(), time.time()))
