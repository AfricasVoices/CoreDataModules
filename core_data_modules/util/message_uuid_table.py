import json

from core_data_modules.util import IDUtils
from core_data_modules.util.sha_utils import SHAUtils


class MessageUuidTable(object):
    """
    An append-only lookup table of messages to UUIDs.

    Functions which accept messages require dictionaries representing a message in a normalised form for the
    message platform which they come from.
    For example, they might include a de-identified sender, a timezone independent date, and the message text.
    """

    def __init__(self, table=None):
        """
        :param table: An existing dictionary of messages to UUIDs to construct the table from.
        :type table: dict of str -> str
        """
        if table is None:
            table = {}
        self.message_to_uuid = table

    def add_message(self, message):
        """
        Adds a new message to this lookup table and returns a new UUID which is now associated with that message.
        If the message was already in this table, instead returns the existing UUID for that message.

        :param message: Normalised message to add to the lookup table.
        :type message: dict
        :return: UUID for the given message.
        :rtype: str
        """
        stringified = SHAUtils.stringify_dict(message)

        if stringified not in self.message_to_uuid:
            new_uuid = IDUtils.generate_uuid("avf-message-uuid-")
            assert new_uuid not in self.message_to_uuid.values(), \
                "UUID collision occurred. " \
                "This is an extremely rare event. Re-running the program " \
                "should resolve the issue."  # Not handling because so rare.
            self.message_to_uuid[stringified] = new_uuid

        return self.message_to_uuid[stringified]

    def get_uuid(self, message):
        """
        Returns the UUID of a message in this table.
        
        Raises a KeyError if the message was not found in this table.
        
        :param message: Normalised message to return the UUID of.
        :type message: dict
        :return: UUID
        :rtype: str
        """
        stringified = SHAUtils.stringify_dict(message)
        return self.message_to_uuid[stringified]

    def __getitem__(self, message):
        """Alias for get_uuid"""
        return self.get_uuid(message)

    def dumps(self, sort_keys=False):
        """
        Serializes this object to a JSON string.

        :return: Serialized JSON string
        :rtype: str
        """
        return json.dumps(self.message_to_uuid, sort_keys=sort_keys)

    @classmethod
    def loads(cls, s):
        """
        Creates a new MessageUuidTable object from a serialized JSON string produced by self.dumps.

        :param s: Serialized JSON string to import from.
        :type s: str
        :return:
        :rtype: MessageUuidTable
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
        Deserializes a file into an instance of a MessageUuidTable

        :param f: File to read from.
        :type f: file-like
        :return:
        :rtype: MessageUuidTable
        """
        return cls.loads(f.read())

    def __eq__(self, other):
        return self.message_to_uuid == other.message_to_uuid
