import shutil
import tempfile
import unittest
from os import path

from core_data_modules.util import IOUtils


class TestIOUtils(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_ensure_dirs_exist(self):
        IOUtils.ensure_dirs_exist(path.join(self.test_dir, "a/b/c"))
        self.assertTrue(path.exists(path.join(self.test_dir, "a/b/c")))

        IOUtils.ensure_dirs_exist(path.join(self.test_dir, "a/b/d"))
        self.assertTrue(path.exists(path.join(self.test_dir, "a/b/c")))
        self.assertTrue(path.exists(path.join(self.test_dir, "a/b/d")))

    def test_ensure_dirs_exist_for_file(self):
        IOUtils.ensure_dirs_exist_for_file(path.join(self.test_dir, "x/y/test.txt"))
        self.assertTrue(path.exists(path.join(self.test_dir, "x/y")))
        self.assertFalse(path.exists(path.join(self.test_dir, "x/y/test.txt")))

        # Test method doesn't fail if no parent directories provided
        IOUtils.ensure_dirs_exist_for_file(path.join(self.test_dir, "test.txt"))
        IOUtils.ensure_dirs_exist_for_file("test.txt")

