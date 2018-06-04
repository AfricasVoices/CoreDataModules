from setuptools import setup

setup(
    name="CoreDataModules",
    version="0.2.0",
    url="https://github.com/AfricasVoices/CoreDataModules",
    packages=["core_data_modules"],
    setup_requires=["pytest-runner"],
    install_requires=["deprecation", "six", "unicodecsv", "jsonpickle"],
    tests_require=["pytest"]
)
