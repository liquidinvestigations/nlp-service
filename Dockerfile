FROM python:3.9.1-buster

RUN mkdir /opt/app/
WORKDIR /opt/app/

ENV PYTHONPATH="${PYTHONPATH}:/data/spacy"
ENV POLYGLOT_DATA_PATH=/data/

COPY Pipfile Pipfile.lock  ./

RUN pip install pipenv
RUN pipenv install --system --deploy --ignore-pipfile
RUN mkdir /data/


COPY download.py .
COPY entity_extractor ./entity_extractor

COPY runserver .
COPY download .
RUN chmod +x ./runserver
RUN chmod +x ./download

COPY tests ./tests
COPY presets ./presets

ENV FLASK_APP entity_extractor
ENV FLASK_DEBUG 0

ENV NLP_SERVICE_PRESET=full_md
RUN ./download

EXPOSE 5000
CMD /opt/app/runserver
