from setuptools import setup

setup(
    name="CoreDataModules",
    version="0.1",
    url="https://github.com/AfricasVoices/CoreDataModules",
    packages=["core_data_modules"],
    setup_requires=["pytest-runner"],
    install_requires=["deprecation==2.0.2"],
    tests_require=["pytest", "deprecation==2.0.2"]
)
