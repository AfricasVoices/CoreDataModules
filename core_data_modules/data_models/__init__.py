from .scheme import Scheme, Code


# TODO: Delete once implemented properly by Luke
class Message(object):
    message_id = None
    text = None
    creation_date_time_utc = None
    labels = []

    def to_dict(self):
        return {
            "MessageID": self.message_id,
            "Text": self.text,
            "CreationDateTimeUTC": self.creation_date_time_utc,
            "Labels": self.labels
        }


class Label(object):
    scheme_id = None
    code_id = None
    date_time_utc = None
    checked = False
    confidence = None
    # Note: Not supporting label_set
    origin = None

    def to_dict(self):
        return {
            "SchemeID": self.scheme_id,
            "CodeID": self.code_id,
            "DateTimeUTC": self.date_time_utc,
            "Checked": self.checked,
            "Confidence": self.confidence,
            "Origin": self.origin.to_dict()
        }


class Origin(object):
    origin_id = None
    name = None
    origin_type = None
    metadata = dict()

    def to_dict(self):
        return {
            "OriginID": self.origin_id,
            "Name": self.name,
            "OriginType": self.origin_type,
            "Metadata": self.metadata
        }
