import time

import six
import unicodecsv
from core_data_modules.traced_data import TracedData, Metadata


class TracedDataCSVIO(object):
    @staticmethod
    def dump(data, f):
        """TODO"""
        data = list(data)

        headers = set()
        for td in data:
            for key in six.iterkeys(td):
                headers.add(key)  # TODO: Sort somehow? Column name addition order?

        writer = unicodecsv.DictWriter(f, fieldnames=headers)
        writer.writeheader()

        for td in data:
            writer.writerow(dict(td.items()))

    @staticmethod
    def load(f):
        """TODO"""
        # TODO: This doesn't attempt to merge back with an existing Traced Data iterable.
        # TODO: This doesn't necessarily import the columns in the same order as they were exported in.
        csv = unicodecsv.DictReader(f)

        for row in csv:
            yield TracedData(row, Metadata("user", "excel_import", time.time()))
