import time

from core_data_modules.cleaners import Codes
from core_data_modules.traced_data import Metadata


class Consent(object):
    @staticmethod
    def td_has_stop_code(td, keys):
        """
        Returns whether any of the values for the given keys are Codes.STOP in the given TracedData object.
        
        :param td: TracedData object to search for stop codes.
        :type td: TracedData
        :param keys: Keys to check for stop codes in 'td'.
        :type keys: iterable of str
        :return: Whether td contains Codes.STOP in any of the keys in 'keys'.
        :rtype: bool
        """
        for key in keys:
            if td.get(key) == Codes.STOP:
                return True
        return False

    @classmethod
    def determine_consent_withdrawn(cls, user, data, keys, withdrawn_key="consent_withdrawn"):
        """
        Determines whether consent has been withdrawn, by searching for Codes.STOP in the given list of keys.

        TracedData objects where a stop code is found will have the key-value pair <withdrawn_key>: Codes.TRUE
        appended. Codes which do not will have the air <withdrawn_key>: Codes.False appended instead.
        
        Note that this does not actually set any other keys to Codes.STOP. Use Consent.set_stopped for this purpose.

        :param user: Identifier of the user running this program, for TracedData Metadata.
        :type user: str
        :param data: TracedData objects to determine consent for.
        :type data: iterable of TracedData
        :param keys: Keys to check for stop codes.
        :type keys: iterable of str
        :param withdrawn_key: Name of key to use for the consent withdrawn field.
        :type withdrawn_key: str
        """
        for td in data:
            # TODO: Only set withdrawn_key: False if it is not already TRUE.
            # TODO: Or, just don't set it at all.
            td.append_data(
                {withdrawn_key: Codes.TRUE if cls.td_has_stop_code(td, keys) else Codes.FALSE},
                Metadata(user, Metadata.get_call_location(), time.time())
            )

    @staticmethod
    def set_stopped(user, data, withdrawn_key="consent_withdrawn"):
        """
        For each TracedData object in an iterable whose 'withdrawn_key' is Codes.True, sets every other key to
        Codes.STOP. If there is no withdrawn_key, or the value is not Codes.True, that TracedData object is not modified.
        
        Note that this requires the 'withdrawn_key' to have been set for all the TracedData iterables.
        This may be done using Consent.determine_consent_withdrawn.
        TODO: Implement the above TODO in determine_consent_withdrawn then remove/alter this note.

        :param user: Identifier of the user running this program, for TracedData Metadata.
        :type user: str
        :param data: TracedData objects to set to stopped if consent has been withdrawn.
        :type data: iterable of TracedData
        :param withdrawn_key: Key to TODO
        :type withdrawn_key: str
        """
        for td in data:
            if td[withdrawn_key] == Codes.TRUE:
                stop_dict = dict()
                for key in td.keys():
                    stop_dict[key] = Codes.STOP
                td.append_data(stop_dict, Metadata(user, Metadata.get_call_location(), time.time()))
