import time
import uuid
import json


class PhoneNumberLUT(object):
    def __init__(self, table=None):
        if table is None:
            table = {}
        self.table = table

    def add_number(self, number):
        if number not in self.table:
            self.table[number] = str(uuid.uuid4())
        return self.table[number]

    def get_number(self, uuid):
        pass

    def get_uuid(self, number):
        return self.table[number]

    def __getitem__(self, uuid):
        return self.get_number(uuid)

    def dumps(self):
        return json.dumps(self.table)

    @classmethod
    def loads(cls, dumped):
        return cls(json.loads(dumped))


if __name__ == "__main__":
    lut = PhoneNumberLUT()

    print("Times:")

    # Generate 100k UUIDs
    start = time.time()
    for x in range(100000):
        str(uuid.uuid4())
    end = time.time()
    print("Generate 100k UUIDs", end - start)

    # Generate some phone numbers
    numbers = []
    for x in range(100000):
        numbers.append("+44123456" + str(x).zfill(6))

    # Add all of those phone numbers to the LUT.
    start = time.time()
    uuids = []
    for n in numbers:
        uuids.append(lut.add_number(n))
    end = time.time()
    print("Add 100k numbers", end - start)

    # Read all of the numbers in the LUT.
    start = time.time()
    for u in uuids:
        lut.get_number(u)
    end = time.time()
    print("Lookup 100k numbers", end - start)

    # Serialize
    start = time.time()
    dumped = lut.dumps()
    end = time.time()
    print("Serialize to json string", end - start)

    # Deserialize
    start = time.time()
    lut = PhoneNumberLUT.loads(dumped)
    end = time.time()
    print("Deserialize from json string", end - start)
