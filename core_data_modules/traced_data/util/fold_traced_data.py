from core_data_modules.cleaners import Codes
from core_data_modules.traced_data import Metadata
from core_data_modules.util import TimeUtils


class FoldStrategies(object):
    """
    Standard reconciliation functions for use when folding.
    
    All reconciliation functions take two values, apply some logic to produce the
    """
    AMBIVALENT_BINARY_VALUE = "ambivalent"  # TODO: Move to Core

    @staticmethod
    def assert_equal(x, y):
        assert x == y, f"Values should be the same but are different (differing values were '{x}' and '{y}')"
        return x

    @staticmethod
    def concatenate(x, y):
        if x is None:
            return y
        if y is None:
            return x

        return f"{x};{y}"

    @staticmethod
    def _is_control_code(code):
        # TODO: If we move this function to `Codes`, that will reduce the risk of us updating Core but not updating
        #       the body of this function.
        return code in {
            Codes.STOP, Codes.CODING_ERROR, Codes.NOT_REVIEWED, Codes.NOT_INTERNALLY_CONSISTENT,
            Codes.NOT_CODED, Codes.TRUE_MISSING, Codes.SKIPPED, Codes.WRONG_SCHEME, Codes.NOISE_OTHER_CHANNEL, None
        }

    @staticmethod
    def control_code(x, y):
        # Precedence order in case of conflicts; highest precedence first
        precedence_order = [
            Codes.STOP, Codes.CODING_ERROR, Codes.NOT_REVIEWED, Codes.NOT_INTERNALLY_CONSISTENT,
            Codes.NOT_CODED, Codes.TRUE_MISSING, Codes.SKIPPED, Codes.WRONG_SCHEME, Codes.NOISE_OTHER_CHANNEL, None
        ]

        assert x in precedence_order, "value_1 ('{}') not a missing or stop code".format(x)
        assert y in precedence_order, "value_2 ('{}') not a missing or stop code".format(y)

        if precedence_order.index(x) <= precedence_order.index(y):
            return x
        else:
            return y
        
    @staticmethod
    def boolean_or(x, y):
        assert x in {Codes.TRUE, Codes.FALSE}
        assert y in {Codes.TRUE, Codes.FALSE}

        if x == Codes.TRUE or y == Codes.TRUE:
            return Codes.TRUE
        else:
            return Codes.FALSE
        
    @staticmethod
    def matrix(x, y):
        # TODO: Do the pipelines still need this check?
        # if x == Codes.STOP or y == Codes.STOP:
        #     return Codes.STOP
        
        if x == Codes.MATRIX_1 or y == Codes.MATRIX_1:
            return Codes.MATRIX_1
        else:
            return Codes.MATRIX_0

    @classmethod
    def yes_no_amb(cls, x, y):
        if cls._is_control_code(x) and cls._is_control_code(y):
            return cls.control_code(x, y)
        elif cls._is_control_code(x):
            return y
        elif cls._is_control_code(y):
            return x
        elif x == cls.AMBIVALENT_BINARY_VALUE or y == cls.AMBIVALENT_BINARY_VALUE:
            return cls.AMBIVALENT_BINARY_VALUE
        elif x == y:
            return x
        else:
            return cls.AMBIVALENT_BINARY_VALUE
        

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
        :rtype: list of TracedData
        """
        folded_data = []

        for group in groups:
            folded_td = group.pop(0)
            while len(group) > 0:
                folded_td = fold_fn(folded_td, group.pop(0))
            folded_data.append(folded_td)

        return folded_data

    @staticmethod
    def fold_traced_data(user, td_1, td_2, fold_strategies):
        """
        Folds two TracedData objects into a new TracedData object.

        :param user: Identifier of the user running this program, for TracedData Metadata.
        :type user: str
        :param td_1: First TracedData object to fold.
        :type td_1: TracedData
        :param td_2: Second TracedData object to fold.
        :type td_2: TracedData
        :param fold_strategies: Dictionary of TracedData key to the folding strategy to apply to that key.
                                A folding strategy is a function which folds two individual values.
                                Standard folding functions are available at
                                `core_data_modules.traced_data.util.FoldStrategies`.
        :type fold_strategies: dict of str -> (function of (any, any) -> any)
        :return: td_1 folded with td_2.
        :rtype: TracedData
        """
        # Create (shallow) copies of the input TracedData so that we can fold without modifying the arguments.
        # TODO: Is this necessary?
        td_1 = td_1.copy()
        td_2 = td_2.copy()
        
        # Fold the specified keys using the provided fold strategies.
        folded_dict = dict()
        for key, strategy in fold_strategies.items():
            folded_value = strategy(td_1.get(key), td_2.get(key))
            if folded_value is not None:
                folded_dict[key] = folded_value
        td_1.append_data(folded_dict, Metadata(user, Metadata.get_call_location(), TimeUtils.utc_now_as_iso_string()))
        td_2.append_data(folded_dict, Metadata(user, Metadata.get_call_location(), TimeUtils.utc_now_as_iso_string()))

        # Hide any keys which weren't specified in the list of fold strategies.
        # TODO: Add a note about what would happen if we didn't do this?
        # TODO: Do this here or pull this up into the pipelines. If in the pipelines, there would be no 'magic' here
        td_1.hide_keys(set(td_1.keys()) - set(folded_dict.keys()),
                       Metadata(user, Metadata.get_call_location(), TimeUtils.utc_now_as_iso_string()))
        td_2.hide_keys(set(td_2.keys()) - set(folded_dict.keys()),
                       Metadata(user, Metadata.get_call_location(), TimeUtils.utc_now_as_iso_string()))

        # Append one traced data to the other (to ensure we have a record of both histories), and return.
        folded_td = td_1
        folded_td.append_traced_data("folded_with", td_2,
                                     Metadata(user, Metadata.get_call_location(), TimeUtils.utc_now_as_iso_string()))
        
        return folded_td

    @classmethod
    def fold_iterable_of_traced_data(cls, user, data, fold_id_fn, fold_strategies):
        """
        Folds an iterable of TracedData into a new iterable of TracedData.
        
        Objects with the same fold id (as determined by 'fold_id_fn') are folded together into a new TracedData object.
        
        :param user: Identifier of the user running this program, for TracedData Metadata.
        :type user: str
        :param data: TracedData objects to fold.
        :type data: iterable of TracedData
        :param fold_id_fn: Function which generates a fold id for a TracedData object.
                           TracedData objects with the same fold id will be folded into a single, new TracedData object.
        :type fold_id_fn: function of TracedData -> hashable
        :param fold_strategies: Dictionary of TracedData key to the folding strategy to apply to that key.
                                A folding strategy is a function which folds two individual values.
                                Standard folding functions are available at
                                `core_data_modules.traced_data.util.FoldStrategies`.
        :type fold_strategies: dict of str -> (function of (any, any) -> any)
        :return: Folded TracedData objects.
        :rtype: list of TracedData
        """
        return cls.fold_groups(
            cls.group_by(data, fold_id_fn),
            lambda td_1, td_2: cls.fold_traced_data(user, td_1, td_2, fold_strategies)
        )
