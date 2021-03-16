# NLP-Service for entity extraction using spacy or Polyglot depending on the language
The Service provides entities and detects the language of text. Results are served by a flask app with two endpoints:
`entity_extraction`, which returns the entities in the text, the used method/model and the language of the text. You can also add a language in the POST-request, in order to specify, which language should be used by the service.
and
`language_detection`, which runs polyglots language detection and returns it.

### Running the service without Docker
If you want, you can run the service locally, after creating a python environment using `requirements.txt` with, for example, pipenv.
Note that you need to download the Polyglot embeddings!
Polyglot Embeddings will not be stored in the same directory as if you'd start the docker container, which is in
`/root/polyglot_data/ner2`. By default, they will be stored in your home directory on Linux. You can download the embeddings to a directory of your choice by running `polyglot download --dir /YOUR/PATH`. Be sure to change the directory in your config.
For the list of embeddings downloaded by the service (all available), check out the `polyglot download` commands in the Dockerfile.
Spacy embeddings are downloaded into the environment automatically.

You can start start the service from the CLI with your own path to the polyglot data as:
`python app.py PATH/TO/POLYGLOT_DATA/ner2`

### Default config
The default config is added to the service by default. it is renamed to `app.conf`.
For development purposes, copy the default config `default.conf` into `app.conf` and change the `POLY_PATH` if needed.
