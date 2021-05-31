from core_data_modules.data_models import validators


"""
This module contains Python representations of the objects needed to construct entries in a Coda V2 messages file,
and contains functions for validating, serializing, and de-serializing.

The data formats are specified here:
https://github.com/AfricasVoices/CodaV2/blob/master/docs/data_formats.md#messages

Changes to this file will need to be synced with changes to that specification, and with all other uses of that
specification.
"""


def get_latest_labels(labels):
    """
    Returns the latest label assigned to each code scheme.

    :param labels: Labels to search.
    :type labels: list of Label
    """
    latest_labels = []
    seen_scheme_ids = set()
    # Labels are guaranteed to be sorted newest first, so take the first with each unique scheme id.
    for label in labels:
        if label.scheme_id in seen_scheme_ids:
            continue

        seen_scheme_ids.add(label.scheme_id)
        if label.code_id != "SPECIAL-MANUALLY_UNCODED":
            latest_labels.append(label)

    return latest_labels


class Message(object):
    def __init__(self, message_id, text, creation_date_time_utc, labels, sequence_number=None):
        """
        :type message_id: str
        :type text: str
        :type creation_date_time_utc: str
        :type labels: list of Label
        :type sequence_number: int
        """
        self.message_id = message_id
        self.text = text
        self.creation_date_time_utc = creation_date_time_utc
        self.labels = labels
        self.sequence_number = sequence_number

        self.validate()

    @classmethod
    def from_firebase_map(cls, data):
        message_id = data["MessageID"]
        text = data["Text"]
        creation_date_time_utc = data["CreationDateTimeUTC"]

        labels = []
        for label_map in data["Labels"]:
            labels.append(Label.from_firebase_map(label_map))

        sequence_number = data.get("SequenceNumber")

        return cls(message_id, text, creation_date_time_utc, labels, sequence_number)

    def to_firebase_map(self):
        self.validate()

        firebase_labels = []
        for label in self.labels:
            firebase_labels.append(label.to_firebase_map())

        return {
            "MessageID": self.message_id,
            "Text": self.text,
            "CreationDateTimeUTC": self.creation_date_time_utc,
            "Labels": firebase_labels,
            "SequenceNumber": self.sequence_number
        }

    def copy(self):
        return Message.from_firebase_map(self.to_firebase_map())

    # TODO: Revisit the need for this once the TracedData objects-as-values problems are solved
    def to_dict(self):
        return self.to_firebase_map()

    def get_latest_labels(self):
        """
        Returns the latest label assigned to each code scheme.
        """
        return get_latest_labels(self.labels)

    def validate(self):
        validators.validate_string(self.message_id, "message_id")
        validators.validate_string(self.text, "text")
        validators.validate_utc_iso_string(self.creation_date_time_utc, "creation_date_time_utc")
        validators.validate_list(self.labels, "labels")

        for i, label in enumerate(self.labels):
            assert isinstance(label, Label), "self.labels[{}] is not of type Label".format(i)
            label.validate()


class Label(object):
    def __init__(self, scheme_id, code_id, date_time_utc, origin, checked=None, confidence=None, label_set=None):
        """
        :type scheme_id: str
        :type code_id: str
        :type date_time_utc: str
        :type origin: Origin
        :type checked: bool | None
        :type confidence: double | None
        :type label_set: int | None
        """
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

        return ret

    # TODO: Revisit the need for this once the TracedData objects-as-values problems are solved
    def to_dict(self):
        return self.to_firebase_map()

    @classmethod
    def from_dict(cls, d):
        return cls.from_firebase_map(d)

    def validate(self):
        validators.validate_string(self.scheme_id, "scheme_id")
        validators.validate_string(self.code_id, "code_id")
        validators.validate_utc_iso_string(self.date_time_utc, "date_time_utc")

        if self.checked is not None:
            validators.validate_bool(self.checked, "checked")

        if self.confidence is not None:
            # Not type-checking self.confidence is a float, because Firebase can return either an int or a float.
            # Relying on >= and <= not being defined between numeric and non-numeric types to get an 'is-numeric'
            # type-check as a side-effect of the >= and <= tests.
            assert 0 <= self.confidence <= 1, "self.confidence ({}) is not in range [0, 1]".format(self.confidence)

        if self.label_set is not None:
            validators.validate_int(self.label_set, "label_set")

        assert isinstance(self.origin, Origin), "self.origin not of type Origin"
        self.origin.validate()


class Origin(object):
    def __init__(self, origin_id, name, origin_type, metadata=None):
        """
        :type origin_id: str
        :type name: str
        :type origin_type: str
        :type metadata: (dict of str -> str) | None
        """
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
