import json

from core_data_modules.cleaners import PhoneCleaner
from core_data_modules.util import IDUtils


class PhoneNumberUuidTable(object):
    """
    An append-only lookup table for conversion between phone numbers and UUIDs and vice versa.

    Functions which take phone numbers normalise these numbers before performing any further processing.
    Functions which return phone numbers return the normalised form.
    Phone numbers are normalised using core_data_modules.cleaners.PhoneCleaner.normalise_phone.
    """

    def __init__(self, table=None):
        """
        :param table: An existing dictionary of phone numbers to UUIDs to construct the table from.
        :type table: dict of str -> str
        """
        if table is None:
            table = {}
        self.phone_to_uuid = table
        self.uuid_to_phone = {v: k for k, v in table.items()}

    def add_phone(self, phone):
        """
        Adds a new phone number to this lookup table and returns a new UUID which is now associated with that number.
        If the phone number was already in this table, instead returns the existing UUID for that phone number.

        :param phone: Phone number to add to the lookup table
        :type phone: str
        :return: UUID for this phone number
        :rtype: str
        """
        phone = PhoneCleaner.normalise_phone(phone)

        if phone not in self.phone_to_uuid:
            new_uuid = IDUtils.generate_uuid("avf-phone-uuid-")
            assert new_uuid not in self.uuid_to_phone, "UUID collision occurred. " \
                                                       "This is an extremely rare event. Re-running the program " \
                                                       "should resolve the issue."  # Not handling because so rare.
            self.phone_to_uuid[phone] = new_uuid
            self.uuid_to_phone[new_uuid] = phone

        return self.get_uuid(phone)

    def get_uuid(self, phone):
        """
        Returns the UUID of a phone number in this table.

        The given phone number is normalised before looking up the UUID.

        Raises a KeyError if the phone number was not found in this table.

        :param phone: Number to retrieve UUID of.
        :type phone: str
        :return: UUID
        :rtype: str
        """
        phone = PhoneCleaner.normalise_phone(phone)

        return self.phone_to_uuid[phone]

    def get_phone(self, uuid):
        """
        Returns the normalised phone number for the given UUID in this table.

        Raises a KeyError if the UUID was not found in this table.

        >>> table = PhoneNumberUuidTable()
        >>> uuid = table.add_phone("+254 123 123")
        >>> table.get_phone(uuid)
        '254123123'
        >>> table.get_phone("non_existent_id")
        Traceback (most recent call last):
        ...
        KeyError: 'non_existent_id'

        :param uuid: UUID to retrieve phone number of.
        :type uuid: str
        :return: Phone number
        :rtype: str
        """
        return self.uuid_to_phone[uuid]

    def numbers(self):
        """
        Returns all the phone numbers in the table.
        
        Analogous to dict.keys
        """
        return self.phone_to_uuid.keys()

    def uuids(self):
        """
        Returns all the uuids in the table.
        
        Analogous to dict.keys
        """
        return self.uuid_to_phone.keys()

    def dumps(self, sort_keys=False):
        """
        Serializes this object to a JSON string.

        :return: Serialized JSON string
        :rtype: str
        """
        return json.dumps(self.phone_to_uuid, sort_keys=sort_keys)

    @classmethod
    def loads(cls, s):
        """
        Creates a new PhoneNumberToUuidTable object from a serialized JSON string produced by self.dumps.

        :param s: Serialized JSON string to import from.
        :type s: str
        :return:
        :rtype: PhoneNumberUuidTable
        """
        return cls(json.loads(s))

    def dump(self, f, **dumps_args):
        """
        Serializes this object to a file.

        :param f: File to write to.
        :type f: file-like
        :param dumps_args: See arguments to dumps
        :type dumps_args: dict
        """
        f.write(self.dumps(dumps_args))

    @classmethod
    def load(cls, f):
        """
        Deserializes a file into an instance of a PhoneNumberUuidTable

        :param f: File to read from.
        :type f: file-like
        :return:
        :rtype: PhoneNumberUuidTable
        """
        return cls.loads(f.read())

    def __eq__(self, other):
        return self.phone_to_uuid == other.phone_to_uuid and self.uuid_to_phone == other.uuid_to_phone
