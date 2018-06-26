import json
import time

import pytz
import six
from core_data_modules.util import SHAUtils, IDUtils
from dateutil.parser import isoparse


class MessageUuidTable(object):
    def __init__(self, table=None):
        if table is None:
            table = {}
        self.message_to_uuid = table

    def add_message(self, message):
        """

        :param message: Dictionary of minimum set of data
        :type message: dict
        :return:
        :rtype:
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
        stringified = SHAUtils.stringify_dict(message)
        return self.message_to_uuid[stringified]

    def __getitem__(self, message):
        return self.get_uuid(message)

    def uuids(self):
        return self.message_to_uuid.values()

    if six.PY2:
        def iteruuids(self):
            return self.message_to_uuid.itervalues()

    def dumps(self, sort_keys=False):
        return json.dumps(self.message_to_uuid, sort_keys=sort_keys)

    @classmethod
    def loads(cls, s):
        return cls(json.loads(s))

    def dump(self, f, **dumps_args):
        f.write(self.dumps(dumps_args))

    @classmethod
    def load(cls, f):
        return cls.loads(f.read())

    def __eq__(self, other):
        return self.message_to_uuid == other.message_to_uuid

    @staticmethod
    def dict_repr(d, sender_key, date_key, message_key):
        """

        :param d:
        :type d: frozendict-like
        :param sender_key:
        :type sender_key:
        :param date_key:
        :type date_key:
        :param message_key:
        :type message_key:
        :return:
        :rtype:
        """
        return {
            "Sender": d[sender_key],
            # Convert Date to UNIX timestamp in a Python 2-compatible way.
            # Conversion to UTC accounts for timetuple() not preserving timezone information.
            "Date": time.mktime(isoparse(d[date_key]).astimezone(pytz.utc).timetuple()),
            "Message": d[message_key]
        }
