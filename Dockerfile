FROM python:2.7-slim

WORKDIR /app

ADD . /app

CMD python setup.py test --addopts "--junitxml=test_results.xml"
