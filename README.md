# NLP-Service for entity extraction using spacy or Polyglot depending on the language

The Service uses [spacy] as well as [polyglot]. The models need to be
downloaded. Models are downloaded into the `/data` folder inside the container.
Map it outside if you want to acess the downloaded models.


## Example usage

An example of running the docker container may look like this:

```bash
docker run \
  -e  NLP_SERVICE_MODELS_JSON="$(cat ./presets/test_models.json)" \
  -v data:/data \
  -p 5000:5000 \
  liquidinvestigations/nlp-service
```
You can check out `/presets/test_models.json` to see which models are downloaded in
this example.



## Service Routes

- `POST /entity_extraction`

  returns the entities in the text, the used method/model and the language of
  the text. You can add a language in the POST-request, in order to specify,
  which language should be used by the service. You can also add a model to your
  request in two ways:
   - specify a spacy model to use by adding `"model": "spacy_model_name"` to the
     JSON-data in your request.
   - specify a polyglot model by adding `"model": poly_{language_code}` to the
      JSON-data in your request. The language code has to be a two-character
      [ISO 639][iso codes] language code.

- `POST /language_detection`:

  runs polyglots language detection and returns the resulting language code.

- `GET /config`

  returns the content of `NLP_SERVICE_MODELS_JSON`

## Configuration

- `ENV NLP_SERVICE_MODELS_JSON` - JSON containing models to download.

- `ENV NLP_SERVICE_PRESET` - Download models from presets

- `ENV GUNICORN_WORKERS` - number of [Gunicorn workers], defaults to 2

- `ENV GUNICORN_THREADS=30` - number of [Gunicorn Threads], defaults to 30


The Container automatically tries to download all models which are stored in the
environment variable `NLP_SERVICE_MODELS_JSON`, which has to contain
JSON-formatted text with two keys, `"spacy"` and `polyglot`. Both keys need to
contain a list of models for spacy and language codes for polyglot. Examples can
be found in the `presets` directory, where presets for the environment variable
are stored. A list of available spacy models can be found
[here][spacy models]. A list of all languages for which polyglot supports NER
can be found [here][polyglot models].

## Presets

The `presets` directory contains some presets for downloading models in order to
make configuration easier. You can tell the service to download the models from
a preset by
settings the environment variable `NLP_SERVICE_PRESET` to one of the available
preset names (without the prefix `.json`). The presets are

- `full_lg`: all available large spacy models and all polyglot models. 10.7 GiB,

- `full_md`: all available medium spacy models and all polyglot models. 1,9 GiB

- `full_sm`: all available small spacy models and all polyglot models. 1,3 GiB

- `spacy_lg`: all available large spacy models, no polyglot. 9.9 GiB

- `spacy_md`: all available medium spacy models, no polyglot. 1.1 GiB

- `spacy_sm`: all available small spacy models, no polyglot. 542,4 MiB

- `polyglot_full`: all polyglot models available. 809,8 MiB

- `test_models`: the models which are necessary for tests to pass. Small english
  and multilingual spacy model plus English, German and Romanian Polyglot
  models. 126,4 MiB


## Testing

Use the [`drone` client] to run the tests
using Docker:
  ```bash
  ./test.sh
  ```


[spacy]: https://spacy.io/
[polyglot]: https://polyglot/readthedocs.io
[spacymodels]: https://spacy.io/models/
[polyglot models]: https://polyglot.readthedocs.io/en/latest/NamedEntityRecognition.html
[iso codes]: https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
[Gunicorn Workers]: https://docs.gunicorn.org/en/stable/settings.html#worker-processes
[Gunicorn Threads]: https://docs.gunicorn.org/en/stable/settings.html#threads
[`drone` client]: https://docs.drone.io/cli/install/
