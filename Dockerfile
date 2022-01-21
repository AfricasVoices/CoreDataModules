ARG PYTHON_VERSION
FROM python:${PYTHON_VERSION}-slim

RUN pip install pytest

WORKDIR /app
ADD . /app
RUN pip install -e .[mapping]

CMD pytest --doctest-modules --junitxml=test_results.xml
