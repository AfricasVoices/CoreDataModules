FROM python:2.7-slim

WORKDIR /app

ADD . /app

RUN pip install pipenv
RUN pipenv sync

#CMD pipenv run python test_runner.py
#CMD pipenv run pytest --junitxml=test_results.xml
