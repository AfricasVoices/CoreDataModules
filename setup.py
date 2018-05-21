from setuptools import setup

setup(
    name="CoreDataModules",
    version="0.1",
    url="https://github.com/AfricasVoices/CoreDataModules",
    packages=["core_data_modules"],
    setup_requires=["pytest-runner"],
    install_requires=["deprecation", "six", 'unicodecsv'],
    tests_require=["pytest"]
)
