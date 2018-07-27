import os


class IOUtils(object):
    @staticmethod
    def ensure_dirs_exist(path):
        """
        Creates any directories which do not already exist in the given path.

        The path may be to either a directory or to a file.

        :param path: Path to create directories for.
        :type path: str
        """
        if os.path.dirname(path) is not "" and not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
