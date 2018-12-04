from core_data_modules.data_models import validators


class Scheme(object):
    def __init__(self, scheme_id, name, version, codes, documentation=None):
        if documentation is None:
            documentation = dict()

        self.scheme_id = scheme_id
        self.name = name
        self.version = version
        self.codes = codes
        self.documentation = documentation

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
        

class Code:
    code_id = None
    display_text = None
    code_type = None
    control_code = None
    match_values = None
    shortcut = None
    numeric_value = -42
    string_value = None
    visible_in_coda = True
    color = None

    VALID_CODE_TYPES = {"Normal", "Control"}

    @classmethod
    def from_firebase_map(cls, data):
        code = Code()
        code.code_id = validators.validate_string(data["CodeID"], "CodeID")
        code.display_text = validators.validate_string(data["DisplayText"], "DisplayText")
        
        code.code_type = validators.validate_string(data["CodeType"], "CodeType")
        assert code.code_type in cls.VALID_CODE_TYPES, "CodeType '{}' invalid".format(code.code_type)
        if code.code_type == "Control":
            code.control_code = validators.validate_string(data["ControlCode"], "ControlCode")

        if "MatchValues" in data.keys():
            code.match_values = validators.validate_list(data["MatchValues"], "MatchValues")
            for i, match_value in enumerate(code.match_values):
                validators.validate_string(match_value, "MatchValues[{}]".format(i))
        
        if "Shortcut" in data.keys():
            code.shortcut = validators.validate_string(data["Shortcut"], "Shortcut")
        
        code.numeric_value = validators.validate_int(data["NumericValue"], "NumericValue")
        code.string_value = validators.validate_string(data["StringValue"], "StringValue")
        code.visible_in_coda = validators.validate_bool(data["VisibleInCoda"], "VisibleInCoda")
        
        if "Color" in data.keys():
            code.color = validators.validate_string(data["Color"], "Color")
        
        return code

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
        return other.code_id == self.code_id & \
            other.display_text == self.display_text & \
            other.shortcut == self.shortcut & \
            other.numeric_value == self.numeric_value & \
            other.visible_in_coda == self.visible_in_coda & \
            other.color == self.color
    
    def __ne__(self, other):
        return not self.__eq__(other)
