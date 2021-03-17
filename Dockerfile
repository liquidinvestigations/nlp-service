FROM python:3.9.1-buster

WORKDIR /opt/app/
EXPOSE 5001
ADD requirements.txt .
RUN pip install -r requirements.txt
RUN mkdir /root/polyglot_data
RUN polyglot download ner2.en ner2.de  ner2.ar ner2.bg ner2.ca ner2.cs ner2.da ner2.el ner2.es ner2.et ner2.fa ner2.fi ner2.fr ner2.he ner2.hi ner2.hr ner2.hu ner2.id ner2.it ner2.ja ner2.ko ner2.lt ner2.lv ner2.ms ner2.nl ner2.no ner2.pl ner2.pt ner2.ro ner2.ru ner2.sk ner2.sl ner2.sr ner2.sv ner2.th ner2.tl ner2.tr ner2.uk ner2.vi ner2.zh
RUN polyglot download embeddings2.en embeddings2.de embeddings2.ar embeddings2.bg embeddings2.ca embeddings2.cs embeddings2.da  embeddings2.el embeddings2.et embeddings2.fa embeddings2.fi embeddings2.he embeddings2.hi embeddings2.hr embeddings2.hu embeddings2.id embeddings2.ja embeddings2.ko embeddings2.lt embeddings2.lv embeddings2.ms embeddings2.no embeddings2.ro embeddings2.sk embeddings2.sl embeddings2.sr embeddings2.sv embeddings2.th embeddings2.tl embeddings2.tr embeddings2.uk embeddings2.vi embeddings2.zh
ADD app.py .
ADD tests ./tests
ADD config/default.conf ./config/app.conf
ENV FLASK_APP app.py
ENV FLASK_DEBUG 0

CMD gunicorn -b 0.0.0.0:5000 --worker-connections 1000 app:app
