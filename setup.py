from setuptools import setup

setup(
    name="CoreDataModules",
    version="0.15.0",
    python_requires=">=3.6.0",
    url="https://github.com/AfricasVoices/CoreDataModules",
    packages=["core_data_modules"],
    setup_requires=["pytest-runner"],
    install_requires=["python-dateutil", "pytz"],
    extras_require={
        # Version constraints, the explicit reference to scipy, and the backport dependency `importlib_resources` are
        # needed to support python 3.6. If python_requires is bumped to >=3.7.0, these constraints can be removed.
        "mapping": ["numpy<1.20", "scipy<1.6.0", "pandas<1.2.0", "matplotlib", "geopandas", "descartes", "mapclassify",
                    "importlib_resources"]
    },
    tests_require=["pytest<=3.6.4"]
)
