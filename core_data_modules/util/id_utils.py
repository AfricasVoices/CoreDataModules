import uuid


class IDUtils(object):
    @staticmethod
    def generate_uuid(prefix=""):
        """
        Generates a new UUID, optionally with the given prefix.

        :param prefix: String to prefix the generated UUID with
        :type prefix: str
        :return: New UUID
        :rtype: str
        """
        return prefix + str(uuid.uuid4())
