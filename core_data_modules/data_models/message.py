from core_data_modules.data_models import validators


class Message(object):
    def __init__(self, message_id, text, creation_date_time_utc, labels):
        # Note: Ignoring sequence_number
        self.message_id = message_id
        self.text = text
        self.creation_date_time_utc = creation_date_time_utc
        self.labels = labels

        self.validate()

    @classmethod
    def from_firebase_map(cls, data):
        message_id = data["MessageID"]
        text = data["Text"]
        creation_date_time_utc = data["CreationDateTimeUTC"]

        labels = []
        for label_map in data["Labels"]:
            labels.append(Label.from_firebase_map(label_map))

        return cls(message_id, text, creation_date_time_utc, labels)

    def to_firebase_map(self):
        self.validate()

        labels = []
        for label in self.labels:
            labels.append(label.to_firebase_map())

        return {
            "MessageID": self.message_id,
            "Text": self.text,
            "CreationDateTimeUTC": self.creation_date_time_utc,
            "Labels": labels
        }

    # TODO: Delete?
    def to_dict(self):
        return self.to_firebase_map()

    def validate(self):
        validators.validate_string(self.message_id, "message_id")
        validators.validate_string(self.text, "text")
        validators.validate_string(self.creation_date_time_utc, "creation_date_time_utc")
        # TODO: Validate that creation_date_time_utc is an ISO format string?
        validators.validate_list(self.labels, "labels")

        for i, label in enumerate(self.labels):
            assert isinstance(label, Label), "self.labels[{}] is not of type Label".format(i)
            label.validate()


class Label(object):
    def __init__(self, scheme_id, code_id, date_time_utc, origin, checked=None, confidence=None, label_set=None):
        self.scheme_id = scheme_id
        self.code_id = code_id
        self.date_time_utc = date_time_utc
        self.checked = checked
        self.confidence = confidence
        self.label_set = label_set
        self.origin = origin

        self.validate()

    @classmethod
    def from_firebase_map(cls, data):
        scheme_id = data["SchemeID"]
        code_id = data["CodeID"]
        date_time_utc = data["DateTimeUTC"]
        checked = data.get("Checked")
        confidence = data.get("Confidence")
        label_set = data.get("LabelSet")
        origin = Origin.from_firebase_map(data["Origin"])

        return cls(scheme_id, code_id, date_time_utc, origin, checked, confidence, label_set)

    def to_firebase_map(self):
        self.validate()

        ret = {
            "SchemeID": self.scheme_id,
            "CodeID": self.code_id,
            "DateTimeUTC": self.date_time_utc
        }
        
        if self.checked is not None:
            ret["Checked"] = self.checked
            
        if self.confidence is not None:
            ret["Confidence"] = self.confidence
            
        if self.label_set is not None:
            ret["LabelSet"] = self.label_set
            
        ret["Origin"] = self.origin.to_firebase_map()

    def validate(self):
        validators.validate_string(self.scheme_id, "scheme_id")
        validators.validate_string(self.code_id, "code_id")
        validators.validate_string(self.date_time_utc, "date_time_utc")
        # TODO: Validate that date_time_utc is an ISO format string?

        if self.checked is not None:
            validators.validate_bool(self.checked, "checked")

        if self.confidence is not None:
            validators.validate_double(self.confidence, "confidence")

            # TODO: If we keep this line in then we should specify this in the data_formats.md file in CodaV2
            assert 0 <= self.confidence <= 1, "self.confidence ({}) is not in range [0, 1]".format(self.confidence)

        if self.label_set is not None:
            validators.validate_int(self.label_set, "label_set")

        assert isinstance(self.origin, Origin), "self.origin not of type Origin"
        self.origin.validate()


class Origin(object):
    def __init__(self, origin_id, name, origin_type, metadata=None):
        self.origin_id = origin_id
        self.name = name
        self.origin_type = origin_type
        self.metadata = metadata

    @classmethod
    def from_firebase_map(cls, data):
        origin_id = data["OriginID"]
        name = data["Name"]
        origin_type = data["OriginType"]
        metadata = data.get("Metadata")

        return cls(origin_id, name, origin_type, metadata)

    def to_firebase_map(self):
        self.validate()

        ret = {
            "OriginID": self.origin_id,
            "Name": self.name,
            "OriginType": self.origin_type,
        }

        if self.metadata is not None:
            ret["Metadata"] = self.metadata

        return ret

    def validate(self):
        validators.validate_string(self.origin_id, "origin_id")
        validators.validate_string(self.name, "name")
        validators.validate_string(self.origin_type, "origin_type")

        if self.metadata is not None:
            validators.validate_dict(self.metadata, "metadata")
            for k, v in self.metadata.items():
                validators.validate_string(k, "self.metadata key")
                validators.validate_string(v, "self.metadata[{}]".format(v))