FROM python:3.9.1-buster

WORKDIR /opt/app/
ENV PYTHONPATH="${PYTHONPATH}:/data/spacy"
ENV POLYGLOT_DATA_PATH=/data/
ENV GUNICORN_WORKERS=2
ENV GUNICORN_THREADS=30

ADD Pipfile Pipfile.lock download.py ./

ADD runserver /
RUN chmod +x /runserver
RUN pip install pipenv
RUN pipenv install --system --deploy --ignore-pipfile
RUN mkdir /data/

WORKDIR /opt/app/
EXPOSE 5000
ADD app.py .
ADD tests ./tests
ADD presets /presets
ENV FLASK_APP app.py
ENV FLASK_DEBUG 0

CMD /runserver
