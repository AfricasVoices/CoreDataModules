from setuptools import setup

setup(
    name="CoreDataModules",
    version="0.15.4",
    python_requires=">=3.6.0",
    url="https://github.com/AfricasVoices/CoreDataModules",
    packages=["core_data_modules"],
    setup_requires=["pytest-runner"],
    install_requires=["python-dateutil", "pytz", "firebase_admin", "pyparsing==2.4.7"],
    extras_require={
        # Version constraints, the explicit references to scipy and pyproj, and the backport dependency
        # `importlib_resources` are needed to support python 3.6.
        # If python_requires is bumped to >=3.7.0, these constraints can be removed.
        "mapping": ["pyproj<3.1.0", "numpy<1.20", "scipy<1.6.0", "pandas<1.2.0", "matplotlib<3.4.0", "geopandas",
                    "descartes", "mapclassify", "importlib_resources"]
    },
    tests_require=["pytest<=3.6.4"]
)
