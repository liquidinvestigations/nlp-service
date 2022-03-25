import logging
import os
import json
import spacy
import re
from entity_extractor import app
from polyglot.text import Text
from polyglot.detect import Detector
from polyglot.detect.base import UnknownLanguage
from flask import request, jsonify, abort


log = logging.getLogger(__name__)

DOWNLOADED_MODELS = json.loads(os.getenv('NLP_SERVICE_MODELS_JSON'))

# check for loaded spacy languages and store their language code
if 'spacy' in DOWNLOADED_MODELS:
    SPACY_LANGUAGES = set([model.split('_')[0] for model in DOWNLOADED_MODELS['spacy']])
else:
    SPACY_LANGUAGES = set()
if app.config['SPACY_MULTILINGUAL_LAN_CODE'] in SPACY_LANGUAGES:
    SPACY_LANGUAGES.update(app.config['SPACY_MULILINGUAL_LANGUAGES'])


def get_language(text):
    """ Gets the language code of text using Polyglots language detector.

    If the Environment variable NLP_SERVICE_FALLBACK_LANGUAGE is set, it
    will be returned if no language was detectable, instead of returning no
    language.

    Args:
        text: string to process.

    Returns:
        Two character language code.
    """
    try:
        detector = Detector(text)
    except UnknownLanguage:
        return app.config['FALLBACK_LANGUAGE']
    language = detector.language
    if language.code and language.code != 'un' and detector.reliable:
        return detector.language.code
    elif app.config['FALLBACK_LANGUAGE']:
        return app.config['FALLBACK_LANGUAGE']
    else:
        return None


def get_poly_ents(text, lan):
    """Gets entities from text using polyglot.

    In order to get the same representation of entities in Polyglot as in spacy,
    the start and end indexrelative to the actual text has to be calculated.
    Polyglot defines words and uses word indices, while Spacy uses the char
    indices of the input string.

    Args:
        text: string to process
        lan: language to use.

    Returns:
        list of extracted entities.
    """
    poly_text = Text(text, hint_language_code=lan)
    ents = []
    spans = []
    entity_text = list(set([(' '.join(entity), entity.tag.lstrip('I-'))
                            for entity in poly_text.entities]))
    entity_text.sort(key=len, reverse=True)
    for entity in entity_text:
        for match in re.finditer(re.escape(entity[0]), text):
            # the match is only a match if it's not inside another match.
            # Therefore, the entities are ordered by length beforehand.
            if all(not(span[0] <= match.start() <= span[1]) and not
                    (span[0] <= match.end() <= span[1]) for span in spans):
                spans.append((match.start(), match.end()))
                ents.append({'text': entity[0], 'start': match.start(),
                            'end': match.end(), 'type': entity[1]})
    return ents


def get_spacy_ents(text, nlp):
    """Gets entities from text using spacy.

    The label for PERSON is changed in order to be in accordance with polyglot.
    Spacy doesn't like text over SPACY_TEXT_LIMIT chars so the service handles
    such longs text in more batches.

    Args:
        text: string to process.
        nlp: spacy model to use.

    Returns:
        List of extracted entities.
    """
    if (len(text) > app.config['SPACY_TEXT_LIMIT']):
        ents = []
        for i in range(0, len(text), app.config['SPACY_TEXT_LIMIT']):
            ents += get_spacy_ents(text[i:i + app.config['SPACY_TEXT_LIMIT']], nlp)
        return ents
    doc = nlp(text)
    ents = [{'text': ent.text, 'start': ent.start_char,
            'end': ent.end_char,
             'type': 'PER' if ent.label_ == 'PERSON' else ent.label_}
            for ent in doc.ents]
    return ents


def get_spacy_model(lan):
    """Helper function for getting the most appropriate spacy model.

    It assumes that the largest available model should be loaded and
    the multilingual model only if no other model is available.

    Args:
        lan: language code

    Returns:
        Model: Name of the model
        nlp: The loaded Spacy Model
    """
    language_models = [model for model in DOWNLOADED_MODELS['spacy'] if model.startswith(lan)]
    if not language_models:
        model = 'xx_ent_wiki_sm'
        nlp = spacy.load(model)
        return model, nlp
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

    Args:
        text: string to process
        lan: language code
        model: model string from request

    Returns:
        JSON-Response and Status code that the service will send as response.
    """
    if model.startswith('polyglot'):
        lan = model.split('_')[1]
        if not ('polyglot' in DOWNLOADED_MODELS and lan in DOWNLOADED_MODELS['polyglot']):
            return jsonify({'error': f'no polyglot model for language {lan}'}), 500
        ents = get_poly_ents(text, lan)
        return jsonify({'language': lan, 'model': model, 'entities': ents}), 200
    else:
        if not ('spacy' in DOWNLOADED_MODELS and model in DOWNLOADED_MODELS['spacy']):
            return jsonify({'error': f'no spacy model with name {model}'}), 500
        nlp = spacy.load(model)
        ents = get_spacy_ents(text, nlp)
        return jsonify({'language': lan, 'model': model, 'entities': ents}), 200


@app.route('/entity_extraction', methods=['POST'])
def get_entities():
    """Entity extraction endpoint.

    It checks whether it has received a text data and whether a language or an
    actual model was specified by the request. If not, the language is
    determined and the most appropriate model which is installed is used in
    order to extract entities. Spacy models have prioriy over polyglot models.
    Larger spacy models have priority over smalles ones for the same language.
    Spacy's specific language models have priority over the multilingual model.
    A model can also be specified during the request. Either, a spacy model name
    has to be provided, or NER via polyglot with a language by adding
    - "model": "polyglot_{language_code}" to the request.
    It is first checked, whether the model is installed, if not, the server
    will respond with a 500 error.

    Returns:
        Response with JSON. Either a 500 Error and a Reason, or a 200 Code and
        the extracted entities, as well as information about language and which
        model was used.
    """
    if not request.json or 'text' not in request.json:
        log.warning('POST /entity_extraction 400')
        abort(400)
    text = request.json['text']

    if 'language' in request.json:
        lan = request.json['language']
    else:
        lan = get_language(text[:2500])

    if 'model' in request.json:
        model = request.json['model']
        log.warning('POST /entity_extraction ???')
        return get_ents_from_model(text, lan, model)
    elif lan in SPACY_LANGUAGES:
        model, nlp = get_spacy_model(lan)
        ents = get_spacy_ents(text, nlp)
        log.info('POST /entity_extraction 200')
        return jsonify({'language': lan, 'model': model, 'entities': ents}), 200
    elif lan in DOWNLOADED_MODELS['polyglot']:
        model = f'polyglot_{lan}'
        ents = get_poly_ents(text, lan)
        log.info('POST /entity_extraction 200')
        return jsonify({'language': lan, 'model': model, 'entities': ents}), 200
    else:
        log.warning('POST /entity_extraction 500')
        return jsonify({'error': f'no model for text in language {lan}'}), 500


@app.route('/language_detection', methods=['POST'])
def return_language():
    """Gets the language based on the text andreturns it in a response.

    Returns: json response with either the language (200) or error (500)
    """
    if not request.json or 'text' not in request.json:
        log.warning('POST /language_detection 400')
        abort(400)

    language = get_language(request.json['text'])
    if language:
        log.info('POST /language_detection 200')
        return jsonify({'language': language}), 200
    else:
        log.warning('POST /language_detection 500')
        return jsonify({'error': 'could not determine language for text'}, 500)


@app.route('/config', methods=['GET'])
def return_config():
    """Gets the config variable `NLP_SERVICE_MODELS_JSON`

    Returns:
        The content of `NLP_SERVICE_MODELS_JSON` in a flask response.
    """
    log.info('GET /config 200')
    return DOWNLOADED_MODELS, 200


@app.route('/health', methods=['GET'])
def health():
    """Gets a constant message for the health check.

    Returns:
        {'status': 'ok'}
    """
    log.info('GET /config 200')
    return {'status': 'ok'}, 200
