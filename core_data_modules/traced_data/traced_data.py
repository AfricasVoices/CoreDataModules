import inspect
import time
from collections import Mapping, KeysView, ValuesView, ItemsView, Iterator

from core_data_modules.util import TimeUtils
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
    
    def serialize(self):
        return {
            "User": self.user,
            "Source": self.source,
            "Timestamp": self.timestamp
        }

    @classmethod
    def deserialize(cls, d):
        return cls(d["User"], d["Source"], d["Timestamp"])

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
        name = frame[3]

        return "{}:{}:{}".format(f, str(line), name)

    @staticmethod
    def get_function_location(func):
        """
        Returns the location of a function.
        
        >>> def test_function():
        ...     pass
        >>> Metadata.get_function_location(test_function)
        '...core_data_modules/traced_data/traced_data.py:1:test_function'

        :param func: Function to get the location of.
        :type func: function
        :return: Function location in the format 'path/to/file.py:line:function_name'
        :rtype: str
        """
        f = inspect.getmodule(func).__file__
        line = inspect.getsourcelines(func)[1]
        name = func.__name__

        return "{}:{}:{}".format(f, str(line), name)


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
    _TOMBSTONE_VALUE = "#HIDDEN-VALUE-44dce0a0-e79c-48cf-8d8e-ec59137ef0d0"

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
        self._sha = self._sha_with_prev(data, None if _prev is None else _prev._sha)
        self._metadata = metadata

    def get_sha(self):
        return self._sha

    def append_data(self, new_data, new_metadata):
        """
        Updates this object with the provided key-value pairs.

        :param new_data: Data to update this object with
        :type new_data: dict
        :param new_metadata: Metadata about this update
        :type new_metadata: Metadata
        """
        self._prev = TracedData(self._data, self._metadata, self._prev)
        self._data = new_data
        self._sha = self._sha_with_prev(self._data, self._prev._sha)
        self._metadata = new_metadata

    def append_traced_data(self, key_of_appended, traced_data, new_metadata):
        """
        Updates this object with another traced data object.
        
        After the update, all key-values of 'traced_data', and their histories, become available
        to this object.

        :param key_of_appended: Key in this object of the joined TracedData
        :type key_of_appended: str
        :param traced_data: TracedData object to add to this object
        :type traced_data: TracedData
        :param new_metadata: Metadata about this update
        :type new_metadata: Metadata
        """
        # Fail if there are keys in both objects with differing values.
        common_keys = set(self).intersection(set(traced_data))
        for common_key in common_keys:
            assert self[common_key] == traced_data[common_key], \
                "Key '{}' is common to both TracedData objects, but values are different " \
                "(self[common_key] == '{}' but traced_data[common_key] == '{}')".format(
                    common_key, self[common_key], traced_data[common_key])

        self.append_data({key_of_appended: traced_data}, new_metadata)

    def hide_keys(self, keys, new_metadata):
        """
        Hides the given keys from this TracedData.

        Analogous to deleting keys from a Python dictionary, in that hidden keys will not be returned from this
        TracedData, and requests for hidden keys will raise KeyErrors. However, the keys will be preserved in the
        TracedData history.

        :param keys: Keys to hide in this TracedData
        :type keys: iterable of str
        :param new_metadata: Metadata about this update
        :type new_metadata: Metadata
        """
        # Check that all the keys to be hidden are actually in this TracedData.
        for key in keys:
            if key not in self:
                raise KeyError(key)

        self.append_data({k: self._TOMBSTONE_VALUE for k in keys}, new_metadata)

    @staticmethod
    def _replace_traced_with_sha(data):
        """
        Returns a new dictionary containing all the key-value pairs of the input dictionary,
        but with values of type 'TracedData' replaced with their SHA.

        (This produces a serializable version of the input dict).

        :param data: Dictionary to replace TracedData objects with SHAs in
        :type data: dict
        :return: Copy of input dictionary, with TracedData objects replaced with their SHAs
        :rtype: dict
        """
        return {k: v if type(v) != TracedData else v._sha for k, v in data.items()}

    @classmethod
    def _sha_with_prev(cls, data, prev_sha=None):
        """
        Produces a SHA for the given dictionary of key-value pairs and the SHA of a previous TracedData object.

        :param data: TracedData _data to SHA
        :type data: dict
        :param prev_sha: SHA of previous TraceData (optional). If no prev_sha is provided, uses an empty string
        :type prev_sha: str | None
        :return: SHA of inputs, as described above
        :rtype: str
        """
        if prev_sha is None:
            prev_sha = ""

        return SHAUtils.sha_dict({"data": cls._replace_traced_with_sha(data), "prev_sha": prev_sha})

    def __getitem__(self, key):
        if key in self._data:
            if self._data[key] == self._TOMBSTONE_VALUE:
                raise KeyError(key)
            return self._data[key]

        for traced_values in filter(lambda v: type(v) == TracedData, self._data.values()):
            if key in traced_values:
                if traced_values[key] == self._TOMBSTONE_VALUE:
                    raise KeyError(key)
                return traced_values[key]

        if self._prev is not None:
            return self._prev[key]

        raise KeyError(key)

    def get(self, key, default=None):
        if key in self._data:
            if self._data[key] == self._TOMBSTONE_VALUE:
                return default
            return self._data[key]

        for traced_values in filter(lambda v: type(v) == TracedData, self._data.values()):
            if key in traced_values:
                if traced_values[key] == self._TOMBSTONE_VALUE:
                    return default
                return traced_values[key]

        if self._prev is not None:
            return self._prev.get(key, default)

        return default

    def __len__(self):
        return sum(1 for _ in self)

    def __contains__(self, key):
        if key in self._data:
            if self._data[key] == self._TOMBSTONE_VALUE:
                return False
            return True

        for traced_values in filter(lambda v: type(v) == TracedData, self._data.values()):
            if key in traced_values:
                if traced_values[key] == self._TOMBSTONE_VALUE:
                    return False
                return True

        if self._prev is not None:
            return key in self._prev

        return False

    def __iter__(self):
        return _TracedDataKeysIterator(self)

    def keys(self):
        return KeysView(self)

    def values(self):
        return ValuesView(self)

    def items(self):
        return ItemsView(self)

    def __eq__(self, other):
        if type(other) != TracedData:
            return False

        if set(self._data.keys()) != set(other._data.keys()):
            return False

        for key in self._data.keys():
            if self._data[key] != other._data[key]:
                return False

        return self._metadata == other._metadata and self._sha == other._sha and self._prev == other._prev

    def copy(self):
        # Data, Metadata, and prev are read only so no need to recursively copy those.
        return TracedData(self._data, self._metadata, self._prev)

    def get_history(self, key):
        """
        Returns the history of all the values a particular key has been set to, along with the
        hashes of the TracedData object which was updated and the timestamps. The returned list
        will be sorted in ascending order of timestamp.

        :param key: Key to return history of values for.
        :type key: hashable
        :return: List containing the value history for this key, sorted oldest to newest.
                 Each element is a dictionary with the keys {"sha", "value", "time"}.
                 The "sha" field contains the hash of the TracedData object when this value was set.
                 The "value" field contains what this value was actually set to.
                 The "timestamp" field contains when this update was made, using the timestamp from the update Metadata
        :rtype: list of dict
        """
        history = [] if self._prev is None else self._prev.get_history(key)

        for traced_values in filter(lambda v: type(v) == TracedData, self._data.values()):
            history.extend(traced_values.get_history(key))

        if key in self._data:
            history.append({"sha": self._sha, "value": self._data[key], "timestamp": self._metadata.timestamp})

        history.sort(key=lambda x: x["timestamp"])
        return history

    def clear_history(self, user, file_sha):
        """
        Appends the current data in this object, SHAs to the previous TracedData and to the file in which the history
        can be found, then dereferences the previous history.
        
        :param user: Identifier of the user running this program, for TracedData Metadata.
        :type user: str
        :param file_sha: SHA of the file containing the history of this TracedData (and possibly other objects).
        :type file_sha: str
        """
        keep_data = {k: v for k, v in self.items()}

        keep_data["_PrevTracedDataFileSHA"] = file_sha
        keep_data["_PrevTracedDataSHA"] = self._sha

        self.append_data(keep_data, Metadata(user, Metadata.get_call_location(), TimeUtils.utc_now_as_iso_string()))
        self._prev = None
        self._sha = self._sha_with_prev(self._data, None)

    def serialize(self):
        serialized_history = []

        traced_data = self
        while traced_data is not None:
            serialized_history.append(
                {
                    "Data": {k: v for k, v in traced_data._data.items() if type(v) != TracedData},
                    "NestedTracedData": {k: v.serialize() for k, v in traced_data._data.items() if type(v) == TracedData},
                    "SHA": traced_data._sha,
                    "Metadata": traced_data._metadata.serialize(),
                }
            )
            traced_data = traced_data._prev

        return serialized_history

    @classmethod
    def deserialize(cls, serialized_history):
        traced_data = None

        for d in reversed(serialized_history):
            data = d["Data"]
            for k, v in d["NestedTracedData"].items():
                data[k] = cls.deserialize(v)
            sha = d["SHA"]
            metadata = Metadata.deserialize(d["Metadata"])

            if traced_data is None:
                traced_data = cls(data, metadata)
            else:
                traced_data.append_data(data, metadata)
            assert traced_data._sha == sha
        
        return traced_data

    @staticmethod
    def join_iterables(user, join_on_key, data_1, data_2, data_2_label):
        """
        Outer-joins two iterables of TracedData on the given key.

        Note that a particular value of each 'join_on_key' may only appear once in each of data_1 and
        data_2 (i.e. all 'join_on_key' values must be unique in each iterable)
        
        If there are any keys in common between TracedData items sharing the same join_on_key,
        then these keys must also have the same value in both objects.

        :param user: Identifier of the user running this program, for TracedData Metadata
        :type user: str
        :param join_on_key: Key to join data on
        :type join_on_key: str
        :param data_1: TracedData items to join with data2
        :type data_1: iterable of TracedData
        :param data_2: TracedData items to join with data1
        :type data_2: iterable of TracedData
        :param data_2_label: Identifier to use for 'data_2' objects in the appended TracedData.
                             See the 'key_of_appended' argument of append_traced_data for details
        :type data_2_label: str
        :return: data1 outer-joined with data2 on join_on_key
        :rtype: list of TracedData
        """
        data_1_lut = {td[join_on_key]: td for td in data_1}
        data_2_lut = {td[join_on_key]: td for td in data_2}

        assert len(data_1_lut) == len(data_1), "'join_on_key' is not unique in 'data_1'"
        assert len(data_2_lut) == len(data_2), "'join_on_key' is not unique in 'data_2'"

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
            td_1 = td_1.copy()
            td_1.append_traced_data(
                data_2_label,
                td_2,
                Metadata(user, Metadata.get_call_location(), time.time())
            )

            merged_data.append(td_1)

        return merged_data

    @staticmethod
    def update_iterable(user, update_id_key, to_update, updates, updates_label):
        """
        Updates each TracedData in an iterable with the TracedData which has the same id in another iterable.

        If there are any keys in common between TracedData items sharing the same join_on_key,
        then these keys must also have the same value in both objects.

        :param user: Identifier of the user running this program, for TracedData Metadata.
        :type user: str
        :param update_id_key: Key of identifier in both iterables to match TracedData objects on.
        :type update_id_key: str
        :param to_update: Objects to update.
        :type to_update: iterable of TracedData
        :param updates: Objects containing updated data.
        :type updates: iterable of TracedData
        :param updates_label: Identifier to use for 'update' objects in the appended TracedData.
                              See the 'key_of_appended' argument of append_traced_data for details.
        :type updates_label: str
        """
        updates_lut = {update_td[update_id_key]: update_td for update_td in updates}
        assert len(updates_lut) == len(updates), "'update_id_key' is not unique in argument 'updates'"

        for td in to_update:
            if td[update_id_key] not in updates_lut:
                continue

            update_td = updates_lut[td[update_id_key]]
            td.append_traced_data(
                updates_label,
                update_td,
                Metadata(user, Metadata.get_call_location(), time.time())
            )


# noinspection PyProtectedMember
class _TracedDataKeysIterator(Iterator):
    """Iterator over the keys of a TracedData object"""

    def __init__(self, traced_data, seen_keys=None):
        if seen_keys is None:
            seen_keys = set()
        self.traced_data = traced_data
        self.next_keys = iter(traced_data._data)
        self.next_traced_datas = []
        self.seen_keys = seen_keys

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            # Search for a new key in the iterator for the current TracedData instance.
            try:
                while True:
                    key = next(self.next_keys)

                    if self.traced_data._data[key] == TracedData._TOMBSTONE_VALUE:
                        self.seen_keys.add(key)
                        continue

                    # If this key points to another TracedData, add that TracedData to a queue of objects to return 
                    # after returning the other keys
                    if type(self.traced_data[key]) == TracedData:
                        self.next_traced_datas.append(_TracedDataKeysIterator(self.traced_data[key], self.seen_keys))
                        continue

                    if key not in self.seen_keys:
                        self.seen_keys.add(key)
                        return key
            except StopIteration:
                # We ran out of keys with non-TracedData values.
                # Now return all the keys from the TracedData values.
                while len(self.next_traced_datas) > 0:
                    try:
                        return next(self.next_traced_datas[0])
                    except StopIteration:
                        self.next_traced_datas.pop(0)

                # We ran out of keys which we haven't yet returned. Try the prev TracedData.
                self.traced_data = self.traced_data._prev
                if self.traced_data is None:
                    raise StopIteration()
                self.next_keys = iter(self.traced_data._data)
