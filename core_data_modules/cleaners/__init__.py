from .character_cleaner import CharacterCleaner
from .codes import Codes
from .phone_cleaner import PhoneCleaner
from .regex import Regex

import time

from core_data_modules.traced_data import Metadata


class Cleaners(object):
    @classmethod
    def clean_traced_data_iterable(cls, user, data, clean_args):
        for td in data:
            cls.clean_td(user, td, clean_args)

    @staticmethod
    def clean_td(user, td, clean_args):
        cleaned_data = {}

        for args in clean_args:
            raw_column = args["raw"]
            cleaners = args["cleaners"]
            if type(cleaners) != list:
                cleaners = [cleaners]
            clean_column = args.get("clean", "{}_clean".format(raw_column))

            clean = td[raw_column]
            for cleaner in cleaners:
                clean = cleaner(clean)
            cleaned_data[clean_column] = clean

        td.append_data(cleaned_data, Metadata(user, Metadata.get_call_location(), time.time()))
