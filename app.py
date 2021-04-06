import os
import json
import spacy
import re
from polyglot.text import Text
from polyglot.detect import Detector
from flask import Flask, request, jsonify, abort

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

DOWNLOADED_MODELS = json.loads(os.getenv('NLP_SERVICE_MODELS_JSON'))
# check for loaded spacy languages and store their language code
if 'spacy' in DOWNLOADED_MODELS:
    SPACY_LANGUAGES = set([model.split('_')[0] for model in DOWNLOADED_MODELS['spacy']])
else:
    SPACY_LANGUAGES = set()
if 'xx' in SPACY_LANGUAGES:
    SPACY_LANGUAGES.update(['nl', 'en', 'fr', 'de', 'it', 'pl', 'pt', 'ru', 'es'])


def get_language(text):
    """ Function for getting the language code using Polyglots language detector.
    """
    detector = Detector(text)
    language = detector.language
    if language.code and language.code != 'un' and detector.reliable:
        return detector.language.code
    else:
        return None


def get_poly_ents(text, lan):
    """Function for getting entities from Polyglot. In order to get the same
    representation of entities in Polyglot as in spacy, the start and end index
    relative to the actual text has to be calculated. Polyglot defines words and
    uses word indices, while Spacy uses the char indices of the input string.
    """
    poly_text = Text(text, hint_language_code=lan)
    ents = []
    spans = []
    entity_text = list(set([(' '.join(entity), entity.tag.lstrip('I-'))
                            for entity in poly_text.entities]))
    entity_text.sort(key=len, reverse=True)
    for entity in entity_text:
        for match in re.finditer(entity[0], text):
            # the match is only a match if it's not inside another match.
            # Therefore, the entities are ordered by length beforehand.
            if all(not(span[0] <= match.start() <= span[1])
                    and not(span[0] <= match.end() <= span[1]) for span in spans):
                spans.append((match.start(), match.end()))
                ents.append({'text': entity[0], 'start': match.start(),
                            'end': match.end(), 'type': entity[1]})
    return ents


def get_spacy_ents(text, nlp):
    """Processes an input text with a spacy model and returns a list of
    entities.
    The label for PERSON is changed in order to be in accordance with polyglot.
    """
    doc = nlp(text)
    ents = [{'text': ent.text, 'start': ent.start_char,
            'end': ent.end_char,
             'label': 'PER' if ent.label_ == 'PERSON' else ent.label_}
            for ent in doc.ents]
    return ents


def get_spacy_model(lan):
    """Helper function for getting the most appropriate spacy model.
    It assumes that the largest available model should be loaded and
    the multilingual model only if no other model is available.
    """
    language_models = [model for model in DOWNLOADED_MODELS['spacy'] if model.startswith(lan)]
    if not language_models:
        method = 'xx_ent_wiki_sm'
        nlp = spacy.load(method)
        return method, nlp
    for size in ['lg', 'md', 'sm']:
        for model in language_models:
            if model.endswith(size):
                nlp = spacy.load(model)
                return model, nlp


def get_ents_from_model(text, lan, model):
    """Fuction for checking what to do with a requested model.
    For both, polyglot and spacy model first it is checked whether
    they are downloaded. If not, the server with respond with a 500 error.
    If they are downloaded, get the ents and return.
    """
    if model.startswith('poly'):
        lan = model.split('_')[1]
        if 'polyglot' in DOWNLOADED_MODELS and lan in DOWNLOADED_MODELS['polyglot']:
            model = 'polyglot'
            ents = get_poly_ents(text, lan)
            return jsonify({'language': lan, 'model': model, 'entities': ents}), 200
        else:
            return jsonify({'error': f'no polyglot model for language {lan}'}), 500
    else:
        if 'spacy' in DOWNLOADED_MODELS and model in DOWNLOADED_MODELS['spacy']:
            nlp = spacy.load(model)
            ents = get_spacy_ents(text, nlp)
            return jsonify({'language': lan, 'model': model, 'entities': ents}), 200
        else:
            return jsonify({'error': f'no spacy model with name {model}'}), 500


@app.route('/entity_extraction', methods=['POST'])
def get_entities():
    """Entity extraction endpoint.
    It checks whether it has received a text data and whether a language or an
    actual model was specified by the request. If not, the language is
    determined and the most appropriate model which is installed is used in
    order to extract entities. Spacy models have prioriy over polyglot models.
    larger spacy models have priority over smalles ones for the same language.
    Spacy's specific language models have priority over the multilingual model.
    A model can also be specified during the request. Either, a spacy model name
    has to be provided, or NER via polyglot with a language by adding
    - "model": "poly_{language_code}" to the request.
    It is first checked, whether the model is installed, if not, the server
    will respond with a 500 error.
    """
    if not request.json or 'text' not in request.json:
        abort(400)
    text = request.json['text']
    if 'lan' in request.json:
        lan = request.json['lan']
    else:
        lan = get_language(text[:2500])
    if 'model' in request.json:
        model = request.json['model']
        response = get_ents_from_model(text, lan, model)
    elif lan in SPACY_LANGUAGES:
        model, nlp = get_spacy_model(lan)
        ents = get_spacy_ents(text, nlp)
        response = jsonify({'language': lan, 'model': model, 'entities': ents}), 200
    elif lan in DOWNLOADED_MODELS['polyglot']:
        model = 'polyglot'
        ents = get_poly_ents(text, lan)
        response = jsonify({'language': lan, 'model': model, 'entities': ents}), 200
    else:
        response = jsonify({'error': f'no model for text in language {lan}'}), 500
    return response


@app.route('/language_detection', methods=['POST'])
def return_language():
    """ Language Detection endpoint. Gets the language based on the text and
    returns it in a response.
    """
    if not request.json or 'text' not in request.json:
        abort(400)
    language = get_language(request.json['text'])
    if language:
        return jsonify({'language': language}), 200
    else:
        return jsonify({'error': 'could not determine language for text'}, 500)


def get_app():
    "returns the app for testing"
    return app


if __name__ == "__main__":
    app.run()
