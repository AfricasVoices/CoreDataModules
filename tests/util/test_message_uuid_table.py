import unittest

from core_data_modules.util.message_uuid_table import MessageUuidTable


class TestMessageUuidTable(unittest.TestCase):
    message1 = {
        "Date": 1530023625.0,
        "Message": "Hello!",
        "Sender": "avf-phone-id-c4fd6565-a743-4b26-9432-3a80b1500194"
    }

    message2 = {
        "Date": 1530023645.0,
        "Message": "Test",
        "Sender": "avf-phone-id-73fe3afc-7fc1-45c8-b59a-4e20867e0700"
    }

    def test_add_message_get_uuid(self):
        message_table = MessageUuidTable()

        uuid1 = message_table.add_message(self.message1)
        self.assertEqual(uuid1, message_table.get_uuid(self.message1))
        self.assertEqual(uuid1, message_table[self.message1])
        self.assertEqual(uuid1, message_table.add_message(self.message1))

        self.assertRaises(KeyError, lambda: message_table[self.message2])
        self.assertRaises(KeyError, lambda: message_table.get_uuid(self.message2))

        uuid2 = message_table.add_message(self.message2)
        self.assertEqual(uuid2, message_table.get_uuid(self.message2))
        self.assertEqual(uuid2, message_table[self.message2])
        self.assertEqual(uuid2, message_table.add_message(self.message2))

        self.assertEqual(uuid1, message_table.get_uuid(self.message1))
