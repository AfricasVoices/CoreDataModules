import uuid
import json

import six


class PhoneNumberUuidTable(object):
    """
    A Lookup Table for conversion between phone numbers and UUIDs and vice versa.

    Note that phone numbers are only considired equal if they are provided in exactly the same format
    (e.g. the table considers +254123123 and 0123123 to be different).
    """

    def __init__(self, table=None):
        """
        :param table: An existing dictionary of phone numbers to UUIDs to use.
        :type table: dict
        """
        if table is None:
            table = {}
        self.phone_to_uuid = table
        self.uuid_to_phone = {v: k for k, v in table.items()}

    def add_phone(self, phone):
        """
        Adds a new phone number to this lookup table and returns a new UUID for that phone number.
        If the phone number was already in this table, instead returns the existing UUID for that phone number.

        :param phone: Phone number to add to the lookup table
        :type phone: str
        :return: UUID for this phone number
        :rtype: str
        """
        if phone not in self.phone_to_uuid:
            new_uuid = str(uuid.uuid4())
            assert new_uuid not in self.uuid_to_phone, "UUID collision occurred"
            self.phone_to_uuid[phone] = new_uuid
            self.uuid_to_phone[new_uuid] = phone

        return self.get_uuid(phone)

    def get_uuid(self, number):
        """
        Returns the UUID of a phone number in this table.

        Raises a KeyError if the phone number was not found in this table.

        :param number: Number to retrieve UUID of.
        :type number: str
        :return: UUID
        :rtype: str
        """
        return self.phone_to_uuid[number]

    def __getitem__(self, number):
        """
        Returns the UUID of a phone number in this table.

        Raises a KeyError if the phone number was not found in this table.

        :param number: Number to retrieve UUID of.
        :type number: str
        :return: UUID
        :rtype: str
        """
        return self.get_uuid(number)

    def get_phone(self, uuid):
        """
        Returns the phone number for the given UUID in this table.

        Raises a KeyError if the UUID was not found in this table.

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

    if six.PY2:
        def iternumbers(self):
            """
            Returns all the numbers in the table, as an iterator.
            
            Analogous to dict.iterkeys.
            
            :return:
            :rtype:
            """
            return self.phone_to_uuid.iterkeys()

        def iteruuids(self):
            """
            Returns all the uuids in the table, as an iterator.
        
            Analogous to dict.iterkeys
            """
            return self.uuid_to_phone.iterkeys()

    def dumps(self):
        """
        Serializes this object to a JSON string.

        :return: Serialized JSON string
        :rtype: str
        """
        return json.dumps(self.phone_to_uuid)

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

    def dump(self, f):
        """
        Serializes this object to a file.

        :param f: File to write to.
        :type f: file-like
        """
        f.write(self.dumps())

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
