from datetime import datetime

import pytz

from core_data_modules.cleaners import Codes
from core_data_modules.data_models import Label, Origin


class CodeTranslators(object):
    # TODO: Assert these codes are in sync with Standards?
    # TODO: e.g. by asserting that a scheme version listed here matches that in the gender_scheme json file?

    gender_lut = {
        Codes.MALE: "code-63dcde9a",
        Codes.FEMALE: "code-86a4602c",
        Codes.TRUE_MISSING: "code-NA-3498451d",
        Codes.SKIPPED: "code-NS-5334289d",
        Codes.NOT_CODED: "code-NC-11d6bb91",
        Codes.NOT_REVIEWED: "code-NR-03dd5d73"
    }

    @classmethod
    def gender_code_id(cls, gender):
        return cls.gender_lut[gender]

    @staticmethod
    def gender_scheme_id():
        return "Scheme-12cb6f95"

    @staticmethod
    def make_auto_coded_label(scheme_id, code_id, auto_code_fn_name, date_time_utc=None):
        if date_time_utc is None:
            date_time_utc = datetime.now().astimezone(pytz.utc).isoformat()

        label = Label()
        label.scheme_id = scheme_id
        label.code_id = code_id
        label.date_time_utc = date_time_utc
        label.checked = False
        label.confidence = 0  # TODO
        # Skipping label_set for now
        origin = Origin()
        origin.origin_id = "data-pipeline"  # TODO
        origin.name = auto_code_fn_name
        origin.origin_type = "External"

        label.origin = origin

        return label
    
    @staticmethod
    def clean_field(data, raw_field, clean_field, cleaner, scheme_id, code_id_fn):
        for td in data:
            pass
