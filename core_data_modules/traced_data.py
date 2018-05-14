from deprecation import deprecated

import six

from core_data_modules.util.sha_utils import SHAUtils
from core_data_modules.traced_data_views.traced_data_items_view import _TracedDataItemsView
from core_data_modules.traced_data_views.traced_data_keys_view import _TracedDataKeysView
from core_data_modules.traced_data_views.traced_data_values_view import _TracedDataValuesView


class Metadata(object):
    def __init__(self, user, source, timestamp):
        self.user = user
        self.source = source
        self.timestamp = timestamp

    def __eq__(self, other):
        return self.user == other.user and self.source == other.source and self.timestamp == other.timestamp


class TracedData(object):
    def __init__(self, data, metadata, _prev=None):
        self._prev = _prev
        self._data = data
        self._sha = self._sha_with_prev(data, "" if _prev is None else _prev._sha)
        self._metadata = metadata

    @staticmethod
    def _sha_with_prev(data, prev_sha):
        return SHAUtils.sha_dict({"data": data, "prev_sha": prev_sha})

    def __len__(self):
        return sum(1 for _ in six.viewkeys(self))

    def get(self, key, default=None):
        if key in self._data:
            return self._data[key]
        elif self._prev is not None:
            return self._prev.get(key, default)
        else:
            return default

    def __getitem__(self, key):
        return self.get(key)

    def append(self, new_data, new_metadata):
        self._prev = TracedData(self._data, self._metadata, self._prev)
        self._data = new_data
        self._sha = self._sha_with_prev(self._data, self._prev._sha)
        self._metadata = new_metadata

    @deprecated
    def has_key(self, key):
        if self._data.has_key(key):
            return True
        elif self._prev is not None:
            return self._prev.has_key(key)
        else:
            return False

    def __contains__(self, key):
        if key in self._data:
            return True
        elif self._prev is not None:
            return key in self._prev
        else:
            return False

    if six.PY3:
        def items(self):
            return _TracedDataItemsView(self)

        def keys(self):
            return _TracedDataKeysView(self)

        def values(self):
            return _TracedDataValuesView(self)

    if six.PY2:
        def items(self):
            if self._prev is None:
                return self._data.items()
            else:
                prev_items = dict(self._prev.items())
                for (key, value) in self._data.items():
                    prev_items[key] = value
                return prev_items.items()

        def iteritems(self):
            return iter(self.viewitems())

        def viewitems(self):
            return _TracedDataItemsView(self)

        def keys(self):
            if self._prev is None:
                return self._data.keys()
            else:
                prev_items = dict(self._prev.items())
                for (key, value) in self._data.items():
                    prev_items[key] = value
                return prev_items.keys()

        def iterkeys(self):
            return iter(self.viewkeys())

        def viewkeys(self):
            return _TracedDataKeysView(self)

        def values(self):
            if self._prev is None:
                return self._data.values()
            else:
                prev_items = dict(self._prev.items())
                for (key, value) in self._data.items():
                    prev_items[key] = value
                return prev_items.values()

        def itervalues(self):
            return iter(self.viewvalues())

        def viewvalues(self):
            return _TracedDataValuesView(self)

    def __iter__(self):
        return six.iterkeys(self)

    def __eq__(self, other):
        return self._data == other._data and self._metadata == other._metadata and \
               self._sha == other._sha and self._prev == other._prev

    def copy(self):
        # Data, Metadata, and prev are read only so no need to recursively copy those.
        return TracedData(self._data, self._metadata, self._prev)

    def get_history(self, key):
        history = [] if self._prev is None else self._prev.get_history(key)
        if key in self._data:
            history.append({"sha": self._sha, "value": self._data[key]})
        return history
