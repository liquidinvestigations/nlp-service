FROM python:3.9.1-buster

RUN apt-get update -yqq \
&& apt-get install libmecab2 libmecab-dev

RUN mkdir /opt/app/
WORKDIR /opt/app/

ENV PYTHONPATH="${PYTHONPATH}:/data/spacy"
ENV POLYGLOT_DATA_PATH=/data/

ADD extra-requirements.txt Pipfile Pipfile.lock  ./

RUN pip install pipenv
RUN pipenv install --system --deploy --ignore-pipfile
RUN pip install -r extra-requirements.txt
RUN mkdir /data/


ADD download.py .
ADD app.py .
ADD __init__.py .

ADD runserver .
ADD download .
RUN chmod +x ./runserver
RUN chmod +x ./download

ADD tests ./tests
ADD presets ./presets

ENV FLASK_APP app.py
ENV FLASK_DEBUG 0
ENV WORKER_COUNT 8

ENV NLP_SERVICE_PRESET=full_md
RUN ./download

EXPOSE 5000
CMD /opt/app/runserver
