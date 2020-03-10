from setuptools import setup

setup(
    name="CoreDataModules",
    version="0.14.0",
    python_requires=">=3.6.0",
    url="https://github.com/AfricasVoices/CoreDataModules",
    packages=["core_data_modules"],
    setup_requires=["pytest-runner"],
    install_requires=["deprecation", "six", "unicodecsv", "python-dateutil", "pytz"],
    tests_require=["pytest<=3.6.4"]
)
