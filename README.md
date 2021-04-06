# NLP-Service for entity extraction using spacy or Polyglot depending on the language
The Service provides entities and detects the language of text. Results are
served by a flask app with two endpoints:
- `POST /entity_extraction`, which returns the entities in the text, the used
  method/model and the language of the text. You can also add a language in the
  POST-request, in order to specify, which language should be used by the
  service.
- `POST /language_detection`, which runs polyglots language detection and
  returns it.

It uses spacy as well as polyglot. The models need to be downloaded. The
Container automatically tries to download all models which are stored in the
environment variable `NLP_SERVICE_MODELS_JSON`, which has to contain
JSON-formatted text with two keys, `"spacy"` and `polyglot`. Both keys need to
contain a list of models for spacy and language codes for polyglot. An example
can be found at `config/models.json`. This example contains all available
Polyglot languages, the small english model for spacy as well as the
multilingual model for spacy. A list of available spacy models can be found
[here](https://spacy.io/models/). Models are downloaded into the `/data` folder
inside the container. Map it outside if you want to acess the downloaded models.
An example of running the docker container may look like this: `docker run -e
NLP_SERVICE_MODELS_JSON="$(cat ./config/models.json)" -v data:/data
liquidinvestigations/nlp-service:vXX` where XX is the version number, and `data`
is the path to a data folder of your choice.
