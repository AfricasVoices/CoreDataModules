from setuptools import setup

setup(
    name="CoreDataModules",
    version="0.1",
    url="https://github.com/AfricasVoices/CoreDataModules",
    packages=["core_data_modules"],
    setup_requires=["pytest-runner"],
    tests_require=["pytest", "deprecation==2.0.2"]
)
