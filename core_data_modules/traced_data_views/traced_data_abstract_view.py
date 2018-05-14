import six


# noinspection PyProtectedMember
class _AbstractTracedDataIterator(object):
    def __init__(self, traced_data, return_attr):
        self.traced_data = traced_data
        self.return_attr = return_attr
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
                        return self.return_attr((key, value))
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


class _AbstractTracedDataView(object):
    def __init__(self, traced_data):
        self.traced_data = traced_data

    def __len__(self):
        return len(self.traced_data)

    def __contains__(self, item):
        return item in iter(self)
