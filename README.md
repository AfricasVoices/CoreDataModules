# Core Data Modules

[![CircleCI](https://circleci.com/gh/AfricasVoices/experimental_CoreDataModules/tree/master.svg?style=shield)](https://circleci.com/gh/AfricasVoices/experimental_CoreDataModules/tree/master)

The skeleton of an AVF module library, with tests. 
Currently contains a trivial example which cleans gender from English text.

### Testing
All tests are to be written using [unittest](https://docs.python.org/3/library/unittest.html), 
and to be placed in the `tests/` directory.
The structure of the `tests/` directory should match that of `core_data_modules`, with all test scripts prefixed
with `test_` e.g. `test_feature_1.py`.

To run all tests: `$ python setup.py test`.

To run a specific test or test suite: `$ python setup.py test --addopts path/to/test_file.py::TestClass::test_method` 
e.g. `$ python setup.py test --addopts tests/cleaners/english/test_demographic_cleaner.py`.
