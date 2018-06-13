import uuid


class IDUtils(object):
    @staticmethod
    def generate_uuid():
        return str(uuid.uuid4())
