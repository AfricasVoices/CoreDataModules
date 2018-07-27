import os


class IOUtils(object):
    @staticmethod
    def ensure_dirs_exist(path):
        """
        Creates all non-existent directories in the provided path to a directory.

        Essentially an implementation of `$ mkdir -p`.

        :param path: Path to a directory
        :type path: str
        """
        if not os.path.exists(path):
            os.makedirs(path)

    @classmethod
    def ensure_dirs_exist_for_file(cls, path):
        """
        Creates all non-existent directories in the provided path to a file.

        :param path: Path to a file
        :type path: str
        """
        dir_path = os.path.dirname(path)
        if dir_path is not "":
            cls.ensure_dirs_exist(dir_path)
