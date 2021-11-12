from setuptools import setup

setup(
    name="CoreDataModules",
    version="0.16.0",
    python_requires=">=3.7.0",
    url="https://github.com/AfricasVoices/CoreDataModules",
    packages=["core_data_modules"],
    setup_requires=["pytest-runner"],
    install_requires=["firebase_admin", "python-dateutil", "pytz"],
    extras_require={
        "mapping": ["numpy", "pandas", "matplotlib<3.4.0", "geopandas", "descartes", "mapclassify"]
    },
    tests_require=["pytest<=3.6.4"]
)
