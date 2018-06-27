import filecmp
import shutil
import tempfile
import unittest
from os import path

from core_data_modules.util import MessageUuidTable, SHAUtils


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

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

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

    def test_dumps_loads(self):
        message_table = MessageUuidTable()

        message_table.add_message(self.message1)
        message_table.add_message(self.message2)

        dumped = message_table.dumps()
        loaded = message_table.loads(dumped)

        self.assertEqual(message_table, loaded)

    def generate_dump_load_table(self):
        table = {
            SHAUtils.stringify_dict(self.message1): "avf-message-uuid-4bf3388a-039b-4ca7-8789-319cf8ee343c",
            SHAUtils.stringify_dict(self.message2): "avf-message-uuid-62815f71-2721-42a6-856c-9cd66b66d6b5"
        }

        message_table = MessageUuidTable(table)
        self.assertEqual(message_table[self.message1], "avf-message-uuid-4bf3388a-039b-4ca7-8789-319cf8ee343c")
        self.assertEqual(message_table.get_uuid(self.message2), "avf-message-uuid-62815f71-2721-42a6-856c-9cd66b66d6b5")

        return message_table

    def test_dump(self):
        file_path = path.join(self.test_dir, "test_output.json")

        message_table = self.generate_dump_load_table()

        with open(file_path, "w") as f:
            message_table.dump(f, sort_keys=True)

        self.assertTrue(filecmp.cmp(file_path, "tests/util/resources/message_uuid_table_sample.json"))
        
    def test_load(self):
        with open("tests/util/resources/message_uuid_table_sample.json", "r") as f:
            message_table = MessageUuidTable.load(f)

        expected = self.generate_dump_load_table()
        self.assertEqual(message_table, expected)
