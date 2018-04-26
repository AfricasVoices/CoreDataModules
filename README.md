# Core Data Modules

### Testing
All tests are to be written using [unittest](https://docs.python.org/3/library/unittest.html), 
and to be placed in the `tests/` directory.
The structure of the `tests/` directory should match that of `core_data_modules`, with all test scripts prefixed
with `test_` e.g. `test_feature_1.py`.

To run a specific test or test suite: `$ pipenv run python -m unittest <suite/test>` 
e.g. `$ pipenv run python -m unittest test.cleaners.english.test_demographic_cleaner`

To run all tests: `$ pipenv run python -m unittest discover`.
