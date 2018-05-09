ARG PYTHON_VERSION
FROM python:${PYTHON_VERSION}-slim

WORKDIR /app

ADD . /app

CMD python setup.py test --addopts "--junitxml=test_results.xml"
