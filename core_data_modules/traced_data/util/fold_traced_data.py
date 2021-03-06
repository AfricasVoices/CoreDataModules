from core_data_modules.cleaners import Codes
from core_data_modules.traced_data import Metadata
from core_data_modules.util import TimeUtils


class FoldStrategies(object):
    """
    A standard collection of strategies available to use when folding.
    
    All fold strategies are functions that take two values, and apply some logic to those values in order to produce
    a single, folded result.
    """

    @staticmethod
    def assert_equal(x, y):
        """
        Checks that the values are equal, then returns `x`.
        
        :param x: Value to fold.
        :type x: any
        :param y: Value to fold.
        :type y: any
        :return: `x`.
        :rtype: any
        """
        assert x == y, f"Values should be the same but are different (differing values were '{x}' and '{y}')"
        return x

    @staticmethod
    def concatenate(x, y):
        """
        Concatenates x and y, separating them by a semicolon.
        
        If one of the values is None, the other value is returning without adding a semicolon anywhere.
        
        :param x: Value to fold.
        :type x: str | None
        :param y: Value to fold.
        :type y: str | None
        :return: x and y concatenated together, with a semicolon separating them.
        :rtype: str | None
        """
        if x is None:
            return y
        if y is None:
            return x

        return f"{x};{y}"

    @staticmethod
    def control_code_by_precedence(x, y):
        """
        Folds two control codes, by choosing the control code with the highest precedence.

        The precedence order for control codes is defined as follows (highest precedence listed first):
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
        
        :param x: Value to fold.
        :type x: str | None
        :param y: Value to fold.
        :type y: str | None
        :return: Folded control code.
        :rtype: str | None
        """
        # Precedence order in case of conflicts; highest precedence first
        precedence_order = [
            Codes.STOP, Codes.CODING_ERROR, Codes.NOT_REVIEWED, Codes.NOT_INTERNALLY_CONSISTENT,
            Codes.NOT_CODED, Codes.DELETED, Codes.TRUE_MISSING, Codes.SKIPPED, Codes.WRONG_SCHEME,
            Codes.NOISE_OTHER_CHANNEL, None
        ]

        assert x in precedence_order, "value_1 ('{}') not a control code".format(x)
        assert y in precedence_order, "value_2 ('{}') not a control code".format(y)

        if precedence_order.index(x) <= precedence_order.index(y):
            return x
        else:
            return y
        
    @staticmethod
    def boolean_or(x, y):
        """
        Folds boolean codes with a boolean OR operation.
        
        :param x: Value to fold, either Codes.TRUE or Codes.FALSE.
        :type x: str
        :param y: Value to fold, either Codes.TRUE or Codes.FALSE.
        :type y: str
        :return: Codes.TRUE if `x` or `y` is Codes.TRUE, otherwise Codes.FALSE.
        :rtype: str
        """
        assert x in {Codes.TRUE, Codes.FALSE}
        assert y in {Codes.TRUE, Codes.FALSE}

        if x == Codes.TRUE or y == Codes.TRUE:
            return Codes.TRUE
        else:
            return Codes.FALSE
        
    @staticmethod
    def matrix(x, y):
        """
        Folds matrix values such that if either input is Codes.MATRIX_1, returns Codes.MATRIX_1, otherwise returns
        Codes.MATRIX_0
        
        :param x: Value to fold, either Codes.MATRIX_0 or Codes.MATRIX_1.
        :type x: str
        :param y: Value to fold, either Codes.MATRIX_0 or Codes.MATRIX_1.
        :type y: str
        :return: Codes.MATRIX_1 if `x` or `y` is Codes.MATRIX_1, otherwise Codes.MATRIX_0.
        :rtype: str
        """
        assert x in {Codes.MATRIX_0, Codes.MATRIX_1}
        assert y in {Codes.MATRIX_0, Codes.MATRIX_1}

        if x == Codes.MATRIX_1 or y == Codes.MATRIX_1:
            return Codes.MATRIX_1
        else:
            return Codes.MATRIX_0

    @classmethod
    def yes_no_amb(cls, x, y):
        """
        Folds yes/no/ambivalent values.

        :param x: Value to fold, either a yes/no/ambivalent code or a control code.
        :type x: str
        :param y: Value to fold, either a yes/no/ambivalent code or a control code.
        :type y: str
        :return: Folded control code if both codes are control codes,
                 the normal code if one code is a control code and the other a normal code,
                 Codes.YES if both inputs are Codes.YES,
                 Codes.NO if both inputs are Codes.NO,
                 otherwise cls.AMBIVALENT_BINARY_VALUE.
        :rtype: str
        """
        assert x in {Codes.YES, Codes.NO, Codes.AMBIVALENT} or x in Codes.CONTROL_CODES
        assert y in {Codes.YES, Codes.NO, Codes.AMBIVALENT} or y in Codes.CONTROL_CODES

        if x in Codes.CONTROL_CODES and y in Codes.CONTROL_CODES:
            return cls.control_code_by_precedence(x, y)
        elif x in Codes.CONTROL_CODES:
            return y
        elif y in Codes.CONTROL_CODES:
            return x
        elif x == Codes.AMBIVALENT or y == Codes.AMBIVALENT:
            return Codes.AMBIVALENT
        elif x == y:
            return x
        else:
            return Codes.AMBIVALENT

    @staticmethod
    def assert_label_ids_equal(x, y):
        """
        Checks that two serialised labels have the same scheme ids and code ids, then return the newest.

        :param x: Value to fold - a `core_data_modules.data_models.Label` object in serialised form.
        :type x: dict
        :param y: Value to fold - a `core_data_modules.data_models.Label` object in serialised form.
        :type y: dict
        :return: `x`
        :rtype: dict
        """
        assert x["SchemeID"] == y["SchemeID"] and x["CodeID"] == y["CodeID"], \
            f"Labels should have the same SchemeID and CodeID, but at least one of those is different " \
            f"(differing values were {{'SchemeID': '{x['SchemeID']}', 'CodeID': '{x['CodeID']}'}} " \
            f"and {{'SchemeID': '{y['SchemeID']}', 'CodeID': '{y['CodeID']}'}})"
        return x

    @staticmethod
    def list_of_labels(code_scheme, x, y):
        # Ensure the lists contain each 1 code.
        assert len(x) > 0
        assert len(y) > 0

        # Ensure that all the codes in each list belong to the code_scheme
        for label in x + y:
            assert label["SchemeID"] == code_scheme.scheme_id

        # Ensure that if a list contains true missing, it only contains that code.
        for label in x:
            if code_scheme.get_code_with_code_id(label["CodeID"]).control_code == Codes.TRUE_MISSING:
                assert len(x) == 1
        for label in y:
            if code_scheme.get_code_with_code_id(label["CodeID"]).control_code == Codes.TRUE_MISSING:
                assert len(y) == 1
        
        # If both lists only contain true missing, return true missing, otherwise filter out true missing from both lists.
        if len(x) == 1 and code_scheme.get_code_with_code_id(x[0]["CodeID"]).control_code == Codes.TRUE_MISSING and \
                len(y) == 1 and code_scheme.get_code_with_code_id(y[0]["CodeID"]).control_code == Codes.TRUE_MISSING:
            return x
        x = [label for label in x if code_scheme.get_code_with_code_id(label["CodeID"]).control_code != Codes.TRUE_MISSING]
        y = [label for label in y if code_scheme.get_code_with_code_id(label["CodeID"]).control_code != Codes.TRUE_MISSING]

        # Compute the union of both lists, choosing the first label if there are multiple labels with the same code id.
        # Searches for the presence of any NC labels, but does not add them to the union list.
        union = []
        union_code_ids = set()
        nc_label = None
        for label in x + y:
            if code_scheme.get_code_with_code_id(label["CodeID"]).control_code == Codes.NOT_CODED:
                if nc_label is None:
                    nc_label = label
                continue

            if label["CodeID"] in union_code_ids:
                continue

            union.append(label)
            union_code_ids.add(label["CodeID"])

        # If the union list is empty and there was an NC label, return NC.
        if nc_label is not None and len(union) == 0:
            union = [nc_label]
            
        assert len(union) > 0

        return union


class FoldTracedData(object):
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
