from setuptools import setup

setup(
    name="CoreDataModules",
    version="0.5.4",
    url="https://github.com/AfricasVoices/CoreDataModules",
    packages=["core_data_modules"],
    setup_requires=["pytest-runner"],
    install_requires=["deprecation", "six", "unicodecsv", "jsonpickle", "python-dateutil"],
    tests_require=["pytest<=3.6.4"]
)
