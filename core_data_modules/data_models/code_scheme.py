from core_data_modules.data_models import validators


"""
This module contains Python representations of the objects needed to construct entries in a Coda V2 code scheme file,
and contains functions for validating, serializing, and de-serializing.

The data formats are specified here:
https://github.com/AfricasVoices/CodaV2/blob/master/docs/data_formats.md#code-schemes

Changes to this file will need to be synced with changes to that specification, and with all other uses of that
specification.
"""


class CodeScheme(object):
    def __init__(self, scheme_id, name, version, codes, documentation=None):
        self.scheme_id = scheme_id
        self.name = name
        self.version = version
        self.codes = codes
        self.documentation = documentation

        self.validate()

    def get_code_with_code_id(self, code_id):
        for code in self.codes:
            if code.code_id == code_id:
                return code
        raise KeyError("Code scheme '{}' (id '{}') does not contain a code with id '{}'".format(self.name, self.scheme_id, code_id))

    def get_code_with_control_code(self, control_code):
        for code in self.codes:
            if code.code_type == CodeTypes.CONTROL and code.control_code == control_code:
                return code
        raise KeyError("Code scheme '{}' (id '{}') does not contain a code with control code '{}'".format(self.name, self.scheme_id, control_code))

    def get_code_with_meta_code(self, meta_code):
        for code in self.codes:
            if code.code_type == CodeTypes.META and code.meta_code == meta_code:
                return code
        raise KeyError("Scheme '{}' (id '{}') does not contain a code with meta code '{}'".format(self.name, self.scheme_id, meta_code))

    def get_code_with_match_value(self, match_value):
        for code in self.codes:
            if code.match_values is not None and match_value in code.match_values:
                return code
        raise KeyError("Code scheme '{}' (id '{}') does not contain a code with match value '{}'".format(self.name, self.scheme_id, match_value))

    @classmethod
    def from_firebase_map(cls, data):
        scheme_id = data["SchemeID"]
        name = data["Name"]
        version = data["Version"]

        codes = []
        for code_map in data["Codes"]:
            code = Code.from_firebase_map(code_map)
            assert code.code_id not in code_map.keys(), \
                "Non-unique Code Id found in code scheme: {}".format(code.code_id)
            codes.append(code)

        documentation = None
        if "Documentation" in data.keys():
            doc_map = data["Documentation"]
            documentation = {
                "URI": validators.validate_string(doc_map["URI"])
            }

        return cls(scheme_id, name, version, codes, documentation)

    def to_firebase_map(self):
        self.validate()

        ret = {
            "SchemeID": self.scheme_id,
            "Name": self.name,
            "Version": self.version,
            "Codes": []
        }

        for code in self.codes:
            ret["Codes"].append(code.to_firebase_map())

        if self.documentation is not None:
            ret["Documentation"] = self.documentation

        return ret

    def _validate_code_values_unique(self, values, key_name):
        seen = set()
        for v in values:
            assert v not in seen, f"Scheme {self.scheme_id} contains two codes with {key_name} {v}"

    def validate(self):
        validators.validate_string(self.scheme_id, "scheme_id")
        validators.validate_string(self.name, "name")
        validators.validate_string(self.version, "version")

        validators.validate_list(self.codes, "codes")
        for i, code in enumerate(self.codes):
            assert isinstance(code, Code), f"self.codes[{i}] is not of type Code"
            code.validate()

        self._validate_code_values_unique([c.code_id for c in self.codes], "code_id")
        self._validate_code_values_unique([c.numeric_value for c in self.codes], "numeric_value")
        self._validate_code_values_unique([c.string_value for c in self.codes], "string_value")
        self._validate_code_values_unique([c.control_code for c in self.codes if c.code_type == CodeTypes.CONTROL], "control_code")
        self._validate_code_values_unique([c.meta_code for c in self.codes if c.code_type == CodeTypes.META], "meta_code")

        match_values = []
        for code in self.codes:
            match_values.extend(code.match_values)
        self._validate_code_values_unique(match_values, "match value")

        if self.documentation is not None:
            validators.validate_dict(self.documentation, "documentation")
            validators.validate_string(self.documentation["URI"], "documentation[URI]")

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


class CodeTypes:
    NORMAL = "Normal"
    CONTROL = "Control"
    META = "Meta"


class Code:
    VALID_CODE_TYPES = {CodeTypes.NORMAL, CodeTypes.CONTROL, CodeTypes.META}

    def __init__(self, code_id, code_type, display_text, numeric_value, string_value, visible_in_coda, shortcut=None,
                 color=None, match_values=None, control_code=None, meta_code=None):
        self.code_id = code_id
        self.code_type = code_type
        self.control_code = control_code
        self.meta_code = meta_code
        self.display_text = display_text
        self.shortcut = shortcut
        self.numeric_value = numeric_value
        self.string_value = string_value
        self.visible_in_coda = visible_in_coda
        self.color = color
        self.match_values = match_values
        
        self.validate()

    @classmethod
    def from_firebase_map(cls, data):
        code_id = data["CodeID"]
        display_text = data["DisplayText"]
        code_type = data["CodeType"]
        control_code = data.get("ControlCode")
        meta_code = data.get("MetaCode")
        shortcut = data.get("Shortcut")
        numeric_value = data["NumericValue"]
        string_value = data["StringValue"]
        visible_in_coda = data["VisibleInCoda"]
        color = data.get("Color")
        match_values = data.get("MatchValues")

        return cls(code_id, code_type, display_text, numeric_value, string_value, visible_in_coda, shortcut,
                   color, match_values, control_code, meta_code)

    def to_firebase_map(self):
        self.validate()

        ret = {
            "CodeID": self.code_id,
            "DisplayText": self.display_text,
            "CodeType": self.code_type,
            "NumericValue": self.numeric_value,
            "StringValue": self.string_value,
            "VisibleInCoda": self.visible_in_coda
        }

        if self.control_code is not None:
            ret["ControlCode"] = self.control_code

        if self.meta_code is not None:
            ret["MetaCode"] = self.meta_code

        if self.shortcut is not None:
            ret["Shortcut"] = self.shortcut

        if self.color is not None:
            ret["Color"] = self.color

        if self.match_values is not None:
            ret["MatchValues"] = self.match_values

        return ret

    def validate(self):
        validators.validate_string(self.code_id, "code_id")
        validators.validate_string(self.display_text, "display_text")

        validators.validate_string(self.code_type, "code_type")
        assert self.code_type in self.VALID_CODE_TYPES, f"CodeType '{self.code_type}' invalid"
        if self.code_type == CodeTypes.CONTROL:
            validators.validate_string(self.control_code, "control_code")
        if self.code_type == CodeTypes.META:
            validators.validate_string(self.meta_code, "meta_code")

        if self.shortcut is not None:
            validators.validate_string(self.shortcut, "shortcut")
            assert len(self.shortcut) == 1, f"shortcut {self.shortcut} is not a single character"

        validators.validate_int(self.numeric_value, "numeric_value")
        validators.validate_string(self.string_value, "string_value")
        validators.validate_bool(self.visible_in_coda, "visible_in_coda")

        if self.color is not None:
            validators.validate_string(self.color, "color")

        if self.match_values is not None:
            validators.validate_list(self.match_values, "match_values")
            for i, match_value in enumerate(self.match_values):
                validators.validate_string(match_value, f"match_values[{i}]")

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return other.code_id == self.code_id and \
            other.code_type == self.code_type and \
            other.control_code == self.control_code and \
            other.meta_code == self.meta_code and \
            other.display_text == self.display_text and \
            other.shortcut == self.shortcut and \
            other.numeric_value == self.numeric_value and \
            other.string_value == self.string_value and \
            other.visible_in_coda == self.visible_in_coda and \
            other.color == self.color and \
            other.match_values == self.match_values

    def __ne__(self, other):
        return not self.__eq__(other)
