from core_data_modules.data_models import validators
from core_data_modules.util import SHAUtils


class Scheme(object):
    def __init__(self, scheme_id, name, version, codes, documentation=None):
        if documentation is None:
            documentation = dict()

        self.scheme_id = scheme_id
        self.name = name
        self.version = version
        self.codes = codes
        self.documentation = documentation

    def get_code_with_id(self, code_id):
        for code in self.codes:
            if code.code_id == code_id:
                return code
        raise KeyError("Scheme '{}' (id '{}') does not contain a code with id '{}'".format(self.name, self.scheme_id, code_id))

    def get_code_with_control_code(self, control_code):
        for code in self.codes:
            if code.control_code == control_code:
                return code
        raise KeyError("Scheme '{}' (id '{}') does not contain a code with control code '{}'".format(self.name, self.scheme_id, control_code))

    def get_code_with_match_value(self, match_value):
        for code in self.codes:
            if code.match_values is not None and match_value in code.match_values:
                return code
        raise KeyError("Scheme '{}' (id '{}') does not contain a code with match value '{}'".format(self.name, self.scheme_id, match_value))

    @classmethod
    def from_firebase_map(cls, data):
        scheme_id = validators.validate_string(data["SchemeID"])
        name = validators.validate_string(data["Name"])
        version = validators.validate_string(data["Version"])

        codes = []
        for code_map in data["Codes"]:
            code = Code.from_firebase_map(code_map)
            assert code.code_id not in code_map.keys(), \
                "Non-unique Code Id found in scheme: {}".format(code.code_id)
            codes.append(code)

        documentation = None
        if "Documentation" in data.keys():
            doc_map = data["Documentation"]
            documentation = {
                "URI": validators.validate_string(doc_map["URI"])
            }
        
        return cls(scheme_id, name, version, codes, documentation)
    
    def to_firebase_map(self):
        ret = dict()
        ret["SchemeID"] = self.scheme_id
        ret["Name"] = self.name
        ret["Version"] = self.version
        ret["Codes"] = []
        for code in self.codes:
            ret["Codes"].append(code.to_firebase_map())

        if len(self.documentation) > 0:
            ret["Documentation"] = self.documentation
        
        return ret

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return other.scheme_id == self.scheme_id and \
               other.name == self.name and \
               other.version == self.version and \
               other.documentation == self.documentation and \
               other.codes == self.codes

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(SHAUtils.stringify_dict(self.to_firebase_map()))


class Code:
    VALID_CODE_TYPES = {"Normal", "Control"}

    def __init__(self, code_id, code_type, display_text, numeric_value, string_value, visible_in_coda, shortcut=None,
                 color=None, match_values=None, control_code=None):
        self.code_id = code_id
        self.code_type = code_type
        self.control_code = control_code
        self.display_text = display_text
        self.shortcut = shortcut
        self.numeric_value = numeric_value
        self.string_value = string_value
        self.visible_in_coda = visible_in_coda
        self.color = color
        self.match_values = match_values

    @classmethod
    def from_firebase_map(cls, data):
        code_id = validators.validate_string(data["CodeID"], "CodeID")
        display_text = validators.validate_string(data["DisplayText"], "DisplayText")

        code_type = validators.validate_string(data["CodeType"], "CodeType")
        assert code_type in cls.VALID_CODE_TYPES, "CodeType '{}' invalid".format(code_type)
        control_code = None
        if code_type == "Control":
            control_code = validators.validate_string(data["ControlCode"], "ControlCode")

        match_values = None
        if "MatchValues" in data.keys():
            match_values = validators.validate_list(data["MatchValues"], "MatchValues")
            for i, match_value in enumerate(match_values):
                validators.validate_string(match_value, "MatchValues[{}]".format(i))

        shortcut = None
        if "Shortcut" in data.keys():
            shortcut = validators.validate_string(data["Shortcut"], "Shortcut")

        numeric_value = validators.validate_int(data["NumericValue"], "NumericValue")
        string_value = validators.validate_string(data["StringValue"], "StringValue")
        visible_in_coda = validators.validate_bool(data["VisibleInCoda"], "VisibleInCoda")

        color = None
        if "Color" in data.keys():
            color = validators.validate_string(data["Color"], "Color")

        return cls(code_id, code_type, display_text, numeric_value, string_value, visible_in_coda, shortcut,
                   color, match_values, control_code)

    def to_firebase_map(self):
        ret = dict()
        ret["CodeID"] = validators.validate_string(self.code_id, "CodeID")
        ret["DisplayText"] = validators.validate_string(self.display_text, "DisplayText")
        ret["CodeType"] = validators.validate_string(self.code_type, "CodeType")
        assert self.code_type in self.VALID_CODE_TYPES, "CodeType '{}' invalid".format(self.code_type)
        if self.code_type == "Control":
            ret["ControlCode"] = validators.validate_string(self.control_code, "ControlCode")
        if self.match_values is not None:
            ret["MatchValues"] = validators.validate_list(self.match_values, "MatchValues")
            for i, match_value in enumerate(self.match_values):
                validators.validate_string(match_value, "MatchValues[{}]".format(i))
        if self.shortcut is not None:
            ret["Shortcut"] = validators.validate_string(self.shortcut, "Shortcut")
        ret["NumericValue"] = validators.validate_int(self.numeric_value, "NumericValue")
        ret["StringValue"] = validators.validate_string(self.string_value, "StringValue")
        ret["VisibleInCoda"] = validators.validate_bool(self.visible_in_coda, "VisibleInCoda")
        if self.color is not None:
            ret["Color"] = validators.validate_string(self.color, "Color")
        return ret

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return other.code_id == self.code_id and \
            other.code_type == self.code_type and \
            other.control_code == self.control_code and \
            other.display_text == self.display_text and \
            other.shortcut == self.shortcut and \
            other.numeric_value == self.numeric_value and \
            other.string_value == self.string_value and \
            other.visible_in_coda == self.visible_in_coda and \
            other.color == self.color and \
            other.match_values == self.match_values
    
    def __ne__(self, other):
        return not self.__eq__(other)
