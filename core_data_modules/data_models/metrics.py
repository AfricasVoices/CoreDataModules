from core_data_modules.data_models import validators


"""
This module contains Python representations of the objects needed to construct entries in a Coda V2 messages file,
and contains functions for validating, serializing, and de-serializing.

The data formats are specified here:
https://github.com/AfricasVoices/CodaV2/blob/master/docs/data_formats.md#messages

Changes to this file will need to be synced with changes to that specification, and with all other uses of that
specification.
"""


class MessagesMetrics(object):
    def __init__(self, messages_count, messages_with_label, not_coded_messages, wrong_scheme_messages):
        self.messages_count = messages_count
        self.messages_with_label = messages_with_label
        self.not_coded_messages = not_coded_messages
        self.wrong_scheme_messages = wrong_scheme_messages

        self.validate()

    @classmethod
    def from_firebase_map(cls, data):
        messages_count = data["messages_count"]
        messages_with_label = data["messages_with_label"]
        not_coded_messages = data["not_coded_messages"]
        wrong_scheme_messages = data["wrong_scheme_messages"]
        return cls(messages_count, messages_with_label, not_coded_messages, wrong_scheme_messages)

    def to_firebase_map(self):
        self.validate()

        return {
            "messages_count": self.messages_count,
            "messages_with_label": self.messages_with_label,
            "not_coded_messages": self.not_coded_messages,
            "wrong_scheme_messages": self.wrong_scheme_messages
        }

    def validate(self):
        validators.validate_int(self.messages_count, "messages_count")
        validators.validate_int(self.messages_with_label, "messages_with_label")
        validators.validate_int(self.not_coded_messages, "not_coded_messages")
        validators.validate_int(self.wrong_scheme_messages, "wrong_scheme_messages")
