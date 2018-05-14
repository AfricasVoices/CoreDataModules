import collections
import six


from core_data_modules.traced_data_views.traced_data_abstract_view import _AbstractTracedDataIterator, \
    _AbstractTracedDataView


#
# class _TracedDataValuesView(collections.ValuesView):
#     def __init__(self, traced_data):
#         self.traced_data = traced_data
#
#     def __len__(self):
#         return len(self.traced_data)
#
#     def __contains__(self, value):
#         return value in six.itervalues(self.traced_data)
#
#     def __iter__(self):
#         return _AbstractTracedDataIterator(self.traced_data, lambda item: item[1])

class _TracedDataValuesView(collections.ValuesView, _AbstractTracedDataView):
    pass
