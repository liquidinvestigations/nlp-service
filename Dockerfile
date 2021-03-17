FROM liquidinvestigations/nlp-service:latest-base

WORKDIR /opt/app/
EXPOSE 5000
ADD app.py .
ADD tests ./tests
ADD config/default.conf ./config/app.conf
ADD setup.py .
RUN pip install -e .

ENV FLASK_APP app.py
ENV FLASK_DEBUG 0

CMD gunicorn -b 0.0.0.0:5000 --worker-connections 1000 app:app
