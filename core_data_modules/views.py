import collections
import six


# noinspection PyProtectedMember
class _TracedDataKeysIterator(collections.Iterator):
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
                pass

            # If no keys left to try, load the keys from the prev. TracedData instance.
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


class _TracedDataKeysView(collections.KeysView):
    def __init__(self, traced_data):
        self.traced_data = traced_data

    def __iter__(self):
        return _TracedDataKeysIterator(self.traced_data)
