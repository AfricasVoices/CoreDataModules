import collections
import six


# noinspection PyProtectedMember
class _TracedDataValuesIterator(collections.Iterator):
    def __init__(self, traced_data):
        self.traced_data = traced_data
        self.next_items = iter(traced_data._data.items())
        self.seen_keys = set()

    def __iter__(self):
        return self

    def _next_item(self):
        while True:
            # Search for a new key in the iterator for the current TracedData instance.
            try:
                while True:
                    key, value = next(self.next_items)
                    if key not in self.seen_keys:
                        self.seen_keys.add(key)
                        return value
            except StopIteration:
                # We ran out of values which we haven't yet returned. Try the prev TracedData.
                self.traced_data = self.traced_data._prev
                if self.traced_data is None:
                    raise StopIteration()
                self.next_items = iter(self.traced_data._data.items())

    if six.PY2:
        def next(self):
            return self._next_item()

    if six.PY3:
        def __next__(self):
            return self._next_item()


class _TracedDataValuesView(collections.ValuesView):
    def __init__(self, traced_data):
        self.traced_data = traced_data

    def __len__(self):
        return len(self.traced_data)

    def __contains__(self, value):
        return value in six.itervalues(self.traced_data)

    def __iter__(self):
        return _TracedDataValuesIterator(self.traced_data)
