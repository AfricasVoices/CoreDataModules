# Core Data Modules
[![CircleCI](https://circleci.com/gh/AfricasVoices/CoreDataModules/tree/master.svg?style=shield)](https://circleci.com/gh/AfricasVoices/CoreDataModules/tree/master)

A library of reusable AVF functionality and data structures.

It includes the primary data structure in which all runs are stored, helper functions 
for IO and hashing, and the cleaning library.

## Installation
CoreDataModules is not available on PyPI, so must instead be installed from this GitHub repository.
Do so with the following command, setting `<version>` to the tag to install e.g. `v0.0.1`:
```
$ pipenv install -e git+https://www.github.com/AfricasVoices/CoreDataModules@<version>#egg=CoreDataModules

```

## API Overview

#### TracedData
The data format for a batch of runs in the data pipeline is always an `iterable of TracedData`.

A `TracedData` object can be thought of as a "dictionary with data provenance".
It provides the same read interface as a Python `dict`, but writes must be performed using the `append_data` method,
which requires some additional metadata about each update when it is called. `TracedData` objects maintain a complete
record of all previous updates.

To construct a `TracedData` object, read a value, and update value(s):
```python
import time
from core_data_modules.traced_data import TracedData, Metadata

USER = "test_user"

td = TracedData({"age": "20", "language": "english"}, Metadata(USER, Metadata.get_call_location(), time.time()))
print(td["age"])  # 20

td.append_data({"age": "21"}, Metadata(USER, Metadata.get_call_location(), time.time()))
print(td["age"])  # 21
```

CoreDataModules also provides utilites for converting between in-memory `iterables of TracedData` and JSON, CSV, Coda, Coding CSV, and The Interface files.
For example, to save and load a list of `TracedData` objects by serializing to and from JSON:
```python
from core_data_modules.traced_data.io import TracedDataJsonIO

data =  # TODO: assign iterable of TracedData objects

with open("output.json", "w") as f:
    TracedDataJsonIO.export_traced_data_iterable_to_json(data, f)
    
with open("input.json", "r") as f:
    data = TracedDataJsonIO.import_json_to_traced_data_iterable(f)
```

#### Cleaning
All reusable cleaning functions may be used by importing functionality from `core_data_modules.cleaners`.
For example:
```python
from core_data_modules.cleaners.english.demographic_cleaner import DemographicCleaner

DemographicCleaner.clean_gender("woman")  # 'female'
DemographicCleaner.clean_gender("aoeu")  # None
```
Note that cleaners which fail to assign a cleaned value return `None`.

## Development

### Testing
All tests are to be written using [unittest](https://docs.python.org/3/library/unittest.html), 
and to be placed in the `tests/` directory.
The structure of the `tests/` directory should match that of `core_data_modules`, with all test scripts prefixed
with `test_`.
For example, if there is a file at `core_data_modules/package/file.py`, there should be an associated test file
at `tests/package/test_file.py`.

To run all tests: `$ pipenv run python setup.py test --addopts doctest`.

To run a specific test or test suite: 
`$ pipenv run python setup.py test --addopts path/to/test_file.py::TestClass::test_method` 
e.g. `$ pipenv run python setup.py test --addopts tests/cleaners/english/test_demographic_cleaner.py`.

[Circle CI](https://circleci.com/gh/AfricasVoices) automatically runs all tests in both Python 2.7 and 
Python 3.6 whenever a commit is pushed to this repository.
