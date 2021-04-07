# NLP-Service for entity extraction using spacy or Polyglot depending on the language

The Service uses [spacy] as well as
[polyglot]. The models need to be downloaded.
Models are downloaded into the `/data` folder inside the container. Map it
outside if you want to acess the downloaded models.


## Example usage

An example of running the docker container may look like this:

```bash
docker run \
  -e  NLP_SERVICE_MODELS_JSON="$(cat ./config/models.json)" \
  -v data:/data \
  -p 5000:5000 \
  liquidinvestigations/nlp-service
```
You can check out `/config/models.json` to see which models are downloaded in
this example.



## Service Routes

- `POST /entity_extraction`

  returns the entities in the text, the used
  method/model and the language of the text. You can add a language in the
  POST-request, in order to specify, which language should be used by the
  service.
  You can also add a model to your request in two ways:
   - specify a spacy model to use by adding `"model": "spacy_model_name"` to the
     JSON-data in your request.
   - specify a polyglot model by adding `"model": poly_{language_code}`
      to the JSON-data in your request. The language code has to be a two-character [ISO
     639][iso codes]
     language code.

- `POST /language_detection`:

  runs polyglots language detection and returns the resulting language code.

- `GET /config`

  returns the content of `NLP_SERVICE_MODELS_JSON`

## Configuration

- `ENV NLP_SERVICE_MODELS_JSON` - configuration with what models to download.

The Container automatically tries to download all models which are stored in the
environment variable `NLP_SERVICE_MODELS_JSON`, which has to contain
JSON-formatted text with two keys, `"spacy"` and `polyglot`.
Both keys need to contain a list of models for spacy and language codes
for polyglot. An example can be found at `config/models.json`.
This example contains all available Polyglot languages, the small english model
for spacy as well as the multilingual model for spacy.
A list of available spacy models can be found
[here][spacy models]. A list of all languages for which polyglot
supports NER can be found
[here][polyglot models].


## Testing

Use the [`drone` client](https://docs.drone.io/cli/install/) to run the tests
using Docker:
  ```bash
  ./test.sh
  ```


[spacy]: https://spacy.io/
[polyglot]:https://polyglot.readthedocs.io
[spacy models]: https://spacy.io/models/
[polyglot models]:https://polyglot.readthedocs.io/en/latest/NamedEntityRecognition.html
[iso codes]: https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
