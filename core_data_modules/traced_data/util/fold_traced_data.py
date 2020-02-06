import time

from core_data_modules.cleaners import Codes
from core_data_modules.traced_data import Metadata


class FoldTracedData(object):
    AMBIVALENT_BINARY_VALUE = "ambivalent"

    @staticmethod
    def group_by(data, group_id_fn):
        """
        Groups TracedData objects using the provided group id function.

        :param data: TracedData objects to group.
        :type data: iterable of TracedData
        :param group_id_fn: Function which generates a group id for a TracedData object.
                            TracedData objects with the same group id will be placed into the same group.
        :type group_id_fn: function of TracedData -> hashable
        :return: Groups of TracedData objects.
        :rtype: iterable of iterable of TracedData
        """
        grouped_lut = dict()

        for td in data:
            key = group_id_fn(td)
            if key not in grouped_lut:
                grouped_lut[key] = []
            grouped_lut[key].append(td)

        return grouped_lut.values()

    @staticmethod
    def fold_groups(groups, fold_fn):
        """
        Folds the TracedData objects in each group of a list of groups using the provided fold function.

        :param groups: Groups of TracedData objects. The TracedData objects in each group will be folded into a single
                       TracedData object by repeated application of fold_fn.
        :type groups: iterable of iterable of TracedData
        :param fold_fn: Function to use to fold each pair of TracedData objects.
        :type fold_fn: function of (TracedData, TracedData) -> TracedData
        :return: Folded TracedData objects.
        :rtype: iterable of TracedData
        """
        folded_data = []

        group_count = len(groups)
        progress = 0
        for group in groups:
            folded_td = group.pop(0)
            while len(group) > 0:
                folded_td = fold_fn(folded_td, group.pop(0))
            folded_data.append(folded_td)

            progress += 1
            if progress % 1000 == 0:
                print(f"Progress: {progress} / {group_count}")
        print(f"Progress: {group_count} / {group_count}")

        return folded_data

    @staticmethod
    def assert_equal_keys_equal(td_1, td_2, equal_keys):
        """
        Checks that the provided TracedData objects contain exactly the same values for each of the provided keys.

        Raises an AssertionError if mis-matching keys are found, otherwise returns no value and has no side-effect.

        :param td_1: TracedData object to check for value equality.
        :type td_1: TracedData
        :param td_2: TracedData object to check for value equality.
        :type td_2: TracedData
        :param equal_keys: Keys to check for equality in the TracedData objects.
        :type equal_keys: iterable of str
        """
        for key in equal_keys:
            assert td_1.get(key) == td_2.get(key), "Key '{}' should be the same in both td_1 and td_2 but is " \
                                                   "different (has values '{}' and '{}' " \
                                                   "respectively)".format(key, td_1.get(key), td_2.get(key))

    @staticmethod
    def _is_control_code(code):
        return code in {
            Codes.STOP, Codes.CODING_ERROR, Codes.NOT_REVIEWED, Codes.NOT_INTERNALLY_CONSISTENT,
            Codes.NOT_CODED, Codes.TRUE_MISSING, Codes.SKIPPED, Codes.WRONG_SCHEME, Codes.NOISE_OTHER_CHANNEL, None
        }

    @staticmethod
    def reconcile_missing_values(value_1, value_2):
        """
        Reconciles two missing values, by choosing the form of missing value with the highest precedence.

        The precedence order for missing values is defined as follows (highest precedence listed first):
         - Codes.STOP
         - Codes.CODING_ERROR
         - Codes.NOT_REVIEWED
         - Codes.NOT_INTERNALLY_CONSISTENT
         - Codes.NOT_CODED
         - Codes.TRUE_MISSING
         - Codes.SKIPPED
         - Codes.WRONG_SCHEME
         - Codes.NOISE_OTHER_CHANNEL
         - None

        :param value_1: Code to reconcile.
        :type value_1: str
        :param value_2: Code to reconcile.
        :type value_2: str
        :return: Reconciled code.
        :rtype: str
        """
        # Precedence order in case of conflicts; highest precedence first
        precedence_order = [
            Codes.STOP, Codes.CODING_ERROR, Codes.NOT_REVIEWED, Codes.NOT_INTERNALLY_CONSISTENT,
            Codes.NOT_CODED, Codes.TRUE_MISSING, Codes.SKIPPED, Codes.WRONG_SCHEME, Codes.NOISE_OTHER_CHANNEL, None
        ]

        assert value_1 in precedence_order, "value_1 ('{}') not a missing or stop code".format(value_1)
        assert value_2 in precedence_order, "value_2 ('{}') not a missing or stop code".format(value_2)

        if precedence_order.index(value_1) <= precedence_order.index(value_2):
            return value_1
        else:
            return value_2

    @staticmethod
    def reconcile_keys_by_concatenation(user, td_1, td_2, keys, concat_delimiter=";"):
        """
        Sets the given keys in two TracedData objects to the same value by string concatenating the values of each.

        Concatenated values take the form <td_1[key]><concat_delimiter><td_2[key]>.

        :param user: Identifier of the user running this program, for TracedData Metadata.
        :type user: str
        :param td_1: First TracedData object to concatenate the keys with.
                     This value will appear first in the concatenated string i.e. before the concat_delimiter.
        :type td_1: TracedData
        :param td_2: Second TracedData object to concatenate the keys with.
                     This value will appear first in the concatenated string i.e. after the concat_delimiter.
        :type td_2: TracedData
        :param keys: Keys in each TracedData object to concatenate the values of.
        :type keys: iterable of str
        :param concat_delimiter: String to separate the concatenated strings with.
        :type concat_delimiter: str
        """
        concat_dict = dict()

        for key in keys:
            if key in td_1 and key in td_2:
                concat_dict[key] = "{}{}{}".format(td_1[key], concat_delimiter, td_2[key])

        td_1.append_data(concat_dict, Metadata(user, Metadata.get_call_location(), time.time()))
        td_2.append_data(concat_dict, Metadata(user, Metadata.get_call_location(), time.time()))

    @staticmethod
    def reconcile_matrix_keys(user, td_1, td_2, keys):
        """
        Sets given keys in two TracedData objects to the same value, of Codes.MATRIX_1 if the value in either
        of those objects is Codes.MATRIX_1, otherwise sets the values to Codes.MATRIX_0.

        An exception is made for keys ending with Codes.NOT_CODED - in this case, the folded value is Codes.MATRIX_0
        unless the value in both td_1 and td_2 is Codes.MATRIX_1.

        :param user: Identifier of the user running this program, for TracedData Metadata.
        :type user: str
        :param td_1: TracedData object to reconcile the matrix keys of.
        :type td_1: TracedData
        :param td_2: TracedData object to reconcile the matrix keys of.
        :type td_2: TracedData
        :param keys: Keys in each TracedData object to reconcile.
        :type keys: iterable of str
        """
        matrix_dict = dict()

        possible_matrix_values = {Codes.MATRIX_0, Codes.MATRIX_1}
        for key in keys:
            if td_1.get(key) == Codes.STOP or td_2.get(key) == Codes.STOP:
                matrix_dict[key] = Codes.STOP
                continue

            # TODO: Handle the different modes of missing data

            if key.endswith(Codes.NOT_CODED):
                if td_1.get(key) == Codes.MATRIX_0 or td_2.get(key) == Codes.MATRIX_0:
                    matrix_dict[key] = Codes.MATRIX_0
                else:
                    matrix_dict[key] = Codes.MATRIX_1
                continue

            assert td_1.get(key, Codes.MATRIX_0) in possible_matrix_values, \
                "td_1.get('{}') is not '{}' or '{}' (has value '{}')".format(
                    key, Codes.MATRIX_0, Codes.MATRIX_1, td_1.get(key))
            assert td_2.get(key, Codes.MATRIX_0) in possible_matrix_values, \
                "td_2.get('{}') is not '{}' or '{}' (has value '{}')".format(
                    key, Codes.MATRIX_0, Codes.MATRIX_1, td_2.get(key))

            if td_1.get(key) == Codes.MATRIX_1 or td_2.get(key) == Codes.MATRIX_1:
                matrix_dict[key] = Codes.MATRIX_1
            else:
                pass

        td_1.append_data(matrix_dict, Metadata(user, Metadata.get_call_location(), time.time()))
        td_2.append_data(matrix_dict, Metadata(user, Metadata.get_call_location(), time.time()))

    @staticmethod
    def reconcile_boolean_keys(user, td_1, td_2, keys):
        """
        Sets the given keys in two TracedData objects to the same value, of Codes.TRUE if the value in either
        of those objects is Codes.TRUE, otherwise sets the values to Codes.FALSE.

        :param user: Identifier of the user running this program, for TracedData Metadata.
        :type user: str
        :param td_1: TracedData object to reconcile the boolean keys of.
        :type td_1: TracedData
        :param td_2: TracedData object to reconcile the boolean keys of.
        :type td_2: TracedData
        :param keys: Keys in each TracedData object to reconcile.
        :type keys: iterable of str
        """
        bool_dict = dict()

        for key in keys:
            if td_1.get(key) == Codes.TRUE or td_2.get(key) == Codes.TRUE:
                bool_dict[key] = Codes.TRUE
            else:
                bool_dict[key] = Codes.FALSE

        td_1.append_data(bool_dict, Metadata(user, Metadata.get_call_location(), time.time()))
        td_2.append_data(bool_dict, Metadata(user, Metadata.get_call_location(), time.time()))

    # TODO: Support reconciling datetime strings

    @classmethod
    def reconcile_yes_no_keys(cls, user, td_1, td_2, keys):
        """
        Sets the given keys in two TracedData objects to the same yes/no/both value, using the logic given below.

        The value set for each key is:
         - Codes.STOP if either value is Codes.STOP
         - Codes.BOTH if either value is Codes.BOTH
         - Codes.BOTH if one value is Codes.YES and the other value is Codes.NO
         - Codes.YES if both values are Codes.YES
         - Codes.NO if both values are Codes.NO
         - value 1 if value 1 is Codes.YES or Codes.NO, and value 2 is neither Codes.YES nor Codes.NO
         - value 2 if value 2 is Codes.YES or Codes.NO, and value 1 is neither Codes.YES nor Codes.NO
        If none of the above conditions are true, the logic of FoldTracedData.reconcile_missing_values is applied.

        :param user: Identifier of the user running this program, for TracedData Metadata.
        :type user: str
        :param td_1: TracedData object to reconcile the yes/no keys of.
        :type td_1: TracedData
        :param td_2: TracedData object to reconcile the yes/no keys of.
        :type td_2: TracedData
        :param keys: Keys in each TracedData object to reconcile.
        :type keys: iterable of str
        """
        yes_no_dict = dict()

        for key in keys:
            if td_1.get(key) == Codes.STOP or td_2.get(key) == Codes.STOP:
                yes_no_dict[key] = Codes.STOP
            elif td_1.get(key) == Codes.BOTH or td_2.get(key) == Codes.BOTH:
                yes_no_dict[key] = Codes.BOTH
            elif td_1.get(key) in {Codes.YES, Codes.NO} and td_2.get(key) in {Codes.YES, Codes.NO}:
                yes_no_dict[key] = td_1[key] if td_1[key] == td_2[key] else Codes.BOTH
            elif td_1.get(key) in {Codes.YES, Codes.NO}:
                yes_no_dict[key] = td_1[key]
            elif td_2.get(key) in {Codes.YES, Codes.NO}:
                yes_no_dict[key] = td_2[key]
            else:
                yes_no_dict[key] = cls.reconcile_missing_values(td_1.get(key), td_2.get(key))

        td_1.append_data(yes_no_dict, Metadata(user, Metadata.get_call_location(), time.time()))
        td_2.append_data(yes_no_dict, Metadata(user, Metadata.get_call_location(), time.time()))

    @classmethod
    def reconcile_binary_keys(cls, user, td_1, td_2, keys):
        """
        Sets the given keys in two TracedData objects to the same value, using the logic given below.

        The value set for each key is:
         - The result of cls.reconcile_missing_values if both value 1 and value 2 are missing.
         - value 1 if value 2 is a control code and value 1 is not.
         - value 2 if value 1 is a control code and value 2 is not.
         - cls.AMBIVALENT_BINARY_VALUE if value 1 and value 2 are both cls.AMBIVALENT_BINARY_VALUE.
         - the common value if value 1 == value 2.
         - cls.AMBIVALENT_BINARY_VALUE if value 1 and and value 2 differ.

        :param user: Identifier of the user running this program, for TracedData Metadata.
        :type user: str
        :param td_1: TracedData object to reconcile the binary keys of.
        :type td_1: TracedData
        :param td_2: TracedData object to reconcile the binary keys of.
        :type td_2: TracedData
        :param keys: Keys in each TracedData object to reconcile.
        :type keys: iterable of str
        """
        binary_dict = dict()

        for key in keys:
            if cls._is_control_code(td_1.get(key)) and cls._is_control_code(td_2.get(key)):
                binary_dict[key] = cls.reconcile_missing_values(td_1.get(key), td_2.get(key))
            elif cls._is_control_code(td_1.get(key)):
                binary_dict[key] = td_2.get(key)
            elif cls._is_control_code(td_2.get(key)):
                binary_dict[key] = td_1.get(key)
            elif td_1.get(key) == cls.AMBIVALENT_BINARY_VALUE or td_1.get(key) == cls.AMBIVALENT_BINARY_VALUE:
                binary_dict[key] = cls.AMBIVALENT_BINARY_VALUE
            elif td_1.get(key) == td_2.get(key):
                binary_dict[key] = td_1.get(key)
            else:
                binary_dict[key] = cls.AMBIVALENT_BINARY_VALUE

        td_1.append_data(binary_dict, Metadata(user, Metadata.get_call_location(), time.time()))
        td_2.append_data(binary_dict, Metadata(user, Metadata.get_call_location(), time.time()))

    @staticmethod
    def set_keys_to_value(user, td, keys, value="MERGED"):
        """
        Sets the given keys in a TracedData object to the same given value.

        :param user: Identifier of the user running this program, for TracedData Metadata.
        :type user: str
        :param td: TracedData object to set the keys of.
        :type td: TracedData
        :param keys: Keys to set.
        :type keys: iterable of str
        :param value: Value to set each key to.
        :type value: str
        """
        td.append_data({key: value for key in keys}, Metadata(user, Metadata.get_call_location(), time.time()))

    @classmethod
    def fold_traced_data(cls, user, td_1, td_2, equal_keys=frozenset(), concat_keys=frozenset(),
                         matrix_keys=frozenset(), bool_keys=frozenset(), yes_no_keys=frozenset(),
                         binary_keys=frozenset(), concat_delimiter=";"):
        """
        Folds two TracedData object into a new TracedData object.

        Use the '*_keys' parameters to control how different parameters should be reconciled when folding.
        Keys not included in any of these parameters will be set to the value 'MERGED'.

        :param user: Identifier of the user running this program, for TracedData Metadata.
        :type user: str
        :param td_1: First TracedData object to fold.
        :type td_1: TracedData
        :param td_2: Second TracedData object to fold.
        :type td_2: TracedData
        :param equal_keys: Keys to assert are equal, using FoldTracedData.assert_equal_keys_equal
        :type equal_keys: iterable of str
        :param concat_keys: Keys to fold by string concatenation, using FoldTracedData.reconcile_keys_by_concatenation.
                            Concatenated values take the form <td_1[key]><concat_delimiter><td_2[key]>.
        :type concat_keys: iterable of str
        :param matrix_keys: Keys to fold using FoldTracedData.reconcile_matrix_keys.
        :type matrix_keys: iterable of str
        :param bool_keys: Boolean keys, to fold using FoldTracedData.reconcile_boolean_keys.
        :type bool_keys: iterable of str
        :param yes_no_keys: Yes/No keys, to fold using FoldTracedData.reconcile_yes_no_keys.
        :type yes_no_keys: iterable of str
        :param binary_keys: X/Y/ambivalent keys, to fold using FoldTracedData.reconcile_binary_keys.
        :type binary_keys: iterable of str
        :param concat_delimiter: String to separate the concatenated strings with.
        :type concat_delimiter: str
        :return: td_1 folded with td_2.
        :rtype: TracedData
        """
        td_1 = td_1.copy()
        td_2 = td_2.copy()

        cls.assert_equal_keys_equal(td_1, td_2, equal_keys)
        cls.reconcile_keys_by_concatenation(user, td_1, td_2, concat_keys, concat_delimiter)
        cls.reconcile_matrix_keys(user, td_1, td_2, matrix_keys)
        cls.reconcile_boolean_keys(user, td_1, td_2, bool_keys)
        cls.reconcile_yes_no_keys(user, td_1, td_2, yes_no_keys)
        cls.reconcile_binary_keys(user, td_1, td_2, binary_keys)

        equal_keys = set(equal_keys)
        equal_keys.update(concat_keys)
        equal_keys.update(matrix_keys)
        equal_keys.update(bool_keys)
        equal_keys.update(yes_no_keys)
        equal_keys.update(binary_keys)

        cls.set_keys_to_value(user, td_1, set(td_1.keys()) - set(equal_keys))
        cls.set_keys_to_value(user, td_2, set(td_2.keys()) - set(equal_keys))

        folded_td = td_1
        folded_td.append_traced_data("folded_with", td_2, Metadata(user, Metadata.get_call_location(), time.time()))

        return folded_td

    @classmethod
    def fold_iterable_of_traced_data(cls, user, data, fold_id_fn, equal_keys=frozenset(), concat_keys=frozenset(),
                                     matrix_keys=frozenset(), bool_keys=frozenset(), yes_no_keys=frozenset(),
                                     binary_keys=frozenset(), concat_delimiter=";"):
        """
        Folds an iterable of TracedData into a new iterable of TracedData.

        Objects with the same fold id (as determined by 'fold_id_fn') are folded together into a new TracedData object.

        Use the '*_keys' parameters to control how different parameters should be reconciled when folding.
        Keys not included in any of these parameters will be set to the value 'MERGED'.

        :param user: Identifier of the user running this program, for TracedData Metadata.
        :type user: str
        :param data: TracedData objects to fold.
        :type data: iterable of TracedData
        :param fold_id_fn: Function which generates a fold id for a TracedData object.
                           TracedData objects with the same fold id will be folded into a single, new TracedData object.
        :type fold_id_fn: function of TracedData -> hashable
        :param equal_keys: Keys to assert are equal, using FoldTracedData.assert_equal_keys_equal
        :type equal_keys: iterable of str
        :param concat_keys: Keys to fold by string concatenation, using FoldTracedData.reconcile_keys_by_concatenation.
                            Concatenated values take the form <td_1[key]><concat_delimiter><td_2[key]>.
        :type concat_keys: iterable of str
        :param matrix_keys: Keys to fold using FoldTracedData.reconcile_matrix_keys.
        :type matrix_keys: iterable of str
        :param bool_keys: Boolean keys, to fold using FoldTracedData.reconcile_boolean_keys.
        :type bool_keys: iterable of str
        :param yes_no_keys: Yes/No keys, to fold using FoldTracedData.reconcile_yes_no_keys.
        :type yes_no_keys: iterable of str
        :param binary_keys: X/Y/ambivalent keys, to fold using FoldTracedData.reconcile_binary_keys.
        :type binary_keys: iterable of str
        :param concat_delimiter: String to separate the concatenated strings with.
        :type concat_delimiter: str
        :return: Folded TracedData objects.
        :rtype: iterable of TracedData
        """
        return cls.fold_groups(
            cls.group_by(data, fold_id_fn),
            lambda td_1, td_2: cls.fold_traced_data(
                user, td_1, td_2, equal_keys, concat_keys, matrix_keys, bool_keys, yes_no_keys,
                binary_keys, concat_delimiter
            )
        )

