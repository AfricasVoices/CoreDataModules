import inspect
import time
from collections import Mapping, KeysView, ValuesView, ItemsView, Iterator

import six
from deprecation import deprecated

from core_data_modules.util.sha_utils import SHAUtils


class Metadata(object):
    """
    Holds additional information about a TracedData update.

    A TracedData update occurs when new fields are added to a TracedData object, or existing fields are updated.
    """

    def __init__(self, user, source, timestamp):
        """
        :param user: Identifier of the user who requested the update.
        :type user: str
        :param source: Identifier of the program, or similar, which generated the new data.
        :type source: str
        :param timestamp: When the updated data was generated.
        :type timestamp: float
        """
        self.user = user
        self.source = source
        self.timestamp = timestamp

    def __eq__(self, other):
        return self.user == other.user and self.source == other.source and self.timestamp == other.timestamp

    @staticmethod
    def get_call_location():
        """
        Returns the location where this function was called from.

        :return Caller location in the format 'path/to/file.py:line:function_name'
        :rtype: str
        """
        frame = inspect.stack()[1]  # Access the previous frame to find out where this function was called from.
        f = frame[1]
        line = frame[2]
        func = frame[3]
        return "{}:{}:{}".format(f, str(line), func)


class TracedData(Mapping):
    """
    An append-only dictionary with data provenance.

    **Example Usage**

    To construct a TracedData object, provide a dictionary containing the initial (key, value) pairs,
    plus additional metadata which records where this data came from:
    >>> data = {"id": "0", "phone": "01234123123", "gender": "woman"}
    >>> traced_data = TracedData(data, Metadata("user", Metadata.get_call_location(), time.time()))

    Retrieve values by using Python's dict syntax:
    >>> traced_data["id"]
    '0'
    >>> traced_data.get("missing_key", "default")
    'default'

    To update the object, provide a new dictionary containing the (key, value) pairs to update, and new metadata:
    >>> new_data = {"gender": "f", "age": 25}
    >>> traced_data.append_data(new_data, Metadata("user", Metadata.get_call_location(), time.time()))
    >>> traced_data["age"]
    25
    >>> traced_data["gender"]
    'f'
    """

    def __init__(self, data, metadata, _prev=None):
        """
        :param data: Dict containing data to insert.
        :type data: dict
        :param metadata: See core_data_modules.traced_data.Metadata
        :type metadata: Metadata
        :param _prev: Pointer to the previous update. Not for external use.
        :type _prev: TracedData
        """
        self._prev = _prev
        self._data = data
        self._sha = self._sha_with_prev(data, "" if _prev is None else _prev._sha)
        self._metadata = metadata

    def append_data(self, new_data, new_metadata):
        self._prev = TracedData(self._data, self._metadata, self._prev)
        self._data = new_data
        self._sha = self._sha_with_prev(self._data, self._prev._sha)
        self._metadata = new_metadata

    @staticmethod
    def _sha_with_prev(data, prev_sha):
        return SHAUtils.sha_dict({"data": data, "prev_sha": prev_sha})

    def __getitem__(self, key):
        if key in self._data:
            return self._data[key]
        elif self._prev is not None:
            return self._prev[key]
        else:
            raise KeyError(key)

    def get(self, key, default=None):
        if key in self._data:
            return self._data[key]
        elif self._prev is not None:
            return self._prev.get(key, default)
        else:
            return default

    def __len__(self):
        return sum(1 for _ in self)

    def __contains__(self, key):
        if key in self._data:
            return True
        elif self._prev is not None:
            return key in self._prev
        else:
            return False

    def __iter__(self):
        return _TracedDataKeysIterator(self)

    if six.PY2:
        @deprecated(deprecated_in="v0")
        def has_key(self, key):
            return key in self

        def keys(self):
            return list(self)

        def values(self):
            return [self[key] for key in self]

        def items(self):
            return [(key, self[key]) for key in self]

        def iterkeys(self):
            return iter(self)

        def itervalues(self):
            for key in self:
                yield self[key]

        def iteritems(self):
            for key in self:
                yield (key, self[key])

        def viewkeys(self):
            return KeysView(self)

        def viewvalues(self):
            return ValuesView(self)

        def viewitems(self):
            return ItemsView(self)

    if six.PY3:
        def keys(self):
            return KeysView(self)

        def values(self):
            return ValuesView(self)

        def items(self):
            return ItemsView(self)

    def __eq__(self, other):
        return self._data == other._data and self._metadata == other._metadata and \
               self._sha == other._sha and self._prev == other._prev

    def copy(self):
        # Data, Metadata, and prev are read only so no need to recursively copy those.
        return TracedData(self._data, self._metadata, self._prev)

    def get_history(self, key):
        """
        Returns the history of all the values a particular key has been set to, along with the
        hashes of the TracedData object which was updated.

        :param key: Key to return history of values for.
        :type key: hashable
        :return: List containing the value history for this key, sorted oldest to newest.
                 Each element is a dictionary with the keys {"sha", "value"}.
                 The "sha" field gives the hash of the TracedData object when this value was set.
                 The "value" field gives what this value was actually set to.
        :rtype: list of dict of (hashable, any)
        """
        history = [] if self._prev is None else self._prev.get_history(key)
        if key in self._data:
            history.append({"sha": self._sha, "value": self._data[key]})
        return history

    @staticmethod
    def join_iterables(user, join_on_key, data_1, data_2):
        """
        Outer-joins two iterables of TracedData on the given key.

        Note that a particular value of each 'join_on_key' may only appear once in each of data_1 and
        data_2 (i.e. all 'join_on_key' values must be unique in each iterable)
        
        If there are any keys in common between TracedData items sharing the same join_on_key,
        then these keys must also have the same value in both objects.

        :param user: Identifier of user running this program
        :type user: str
        :param join_on_key: Key to join data on
        :type join_on_key: str
        :param data_1: TracedData items to join with data2
        :type data_1: iterable of TracedData
        :param data_2: TracedData items to join with data1
        :type data_2: iterable of TracedData
        :return: data1 outer-joined with data2 on join_on_key
        :rtype: list of TracedData
        """
        data_1_lut = {td[join_on_key]: td for td in data_1}
        data_2_lut = {td[join_on_key]: td for td in data_2}

        assert len(data_1_lut) == len(data_1), "join_on_key is not unique in data_1"
        assert len(data_2_lut) == len(data_2), "join_on_key is not unique in data_2"

        data_1_ids = set(data_1_lut.keys())
        data_2_ids = set(data_2_lut.keys())

        ids_in_data1_only = data_1_ids - data_2_ids
        ids_in_data2_only = data_2_ids - data_1_ids
        ids_in_both = data_1_ids.intersection(data_2_ids)

        merged_data = []
        for id in ids_in_data1_only:
            merged_data.append(data_1_lut[id])
        for id in ids_in_data2_only:
            merged_data.append(data_2_lut[id])
        for id in ids_in_both:
            td_1 = data_1_lut[id]
            td_2 = data_2_lut[id]

            # Assert all keys in common between the two TracedData items here have identical values.
            common_keys = set(td_1.keys()).intersection(td_2.keys())
            for key in common_keys:
                assert td_1[key] == td_2[key], "TracedData items with the same join_on_key value '{}' have " \
                                               "conflicting values for key '{}' " \
                                               "(value from data_1 is '{}', value from " \
                                               "data_2 is '{}')".format(id, key, td_1[key], td_2[key])

            # Append the data from td_2 to a copy of td_1
            # TODO: Preserve history from both trees.
            td_1 = td_1.copy()
            td_1.append_data(
                dict(td_2.items()),
                Metadata(user, Metadata.get_call_location(), time.time())
            )
            merged_data.append(td_1)

        return merged_data


# noinspection PyProtectedMember
class _TracedDataKeysIterator(Iterator):
    """Iterator over the keys of a TracedData object"""
    def __init__(self, traced_data):
        self.traced_data = traced_data
        self.next_keys = iter(traced_data._data.keys())
        self.seen_keys = set()

    def __iter__(self):
        return self

    def _next_item(self):
        while True:
            # Search for a new key in the iterator for the current TracedData instance.
            try:
                while True:
                    key = next(self.next_keys)
                    if key not in self.seen_keys:
                        self.seen_keys.add(key)
                        return key
            except StopIteration:
                # We ran out of keys which we haven't yet returned. Try the prev TracedData.
                self.traced_data = self.traced_data._prev
                if self.traced_data is None:
                    raise StopIteration()
                self.next_keys = iter(self.traced_data._data.keys())

    if six.PY2:
        def next(self):
            return self._next_item()

    if six.PY3:
        def __next__(self):
            return self._next_item()
