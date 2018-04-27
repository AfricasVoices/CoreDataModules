FROM python:2.7-slim

WORKDIR /app

ADD . /app

RUN pip install pipenv
RUN pipenv sync
RUN mkdir unittest

CMD pipenv run pytest --junitxml=unittest/test_results.xml
