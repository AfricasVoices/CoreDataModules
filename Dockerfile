ARG PYTHON_VERSION
FROM python:${PYTHON_VERSION}-slim

RUN pip install pytest

WORKDIR /app
ADD setup.py /app
RUN mkdir core_data_modules
RUN pip install -e .[mapping]

ADD . /app

CMD pytest --doctest-modules --junitxml=test_results.xml
