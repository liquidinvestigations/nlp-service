FROM python:3.9.1-buster

WORKDIR /opt/app/
EXPOSE 5001
ADD requirements.txt .
RUN pip install -r requirements.txt

ADD app.py .
ENV FLASK_APP app.py
ENV FLASK_DEBUG 0

CMD gunicorn -b 0.0.0.0:5001 --worker-connections 1000 app:app
