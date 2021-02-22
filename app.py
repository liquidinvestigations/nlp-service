import os
import sys
import spacy
import re
from polyglot.text import Text
from polyglot.detect import Detector
from flask import Flask, request, jsonify, abort
nlp = spacy.load('xx_ent_wiki_sm')
nlp_en = spacy.load('en_core_web_sm')
POLY_PATH = "/root/polyglot_data/ner2"
supported_ner_polyglot = [name for name in os.listdir(POLY_PATH)]
supported_ner_spacy = ['nl', 'en', 'fr', 'de', 'it', 'pl', 'pt', 'ru', 'es']
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False


def get_language(text):
    detector = Detector(text)
    language = detector.language
    if language.code and language.code != 'un' and detector.reliable:
        return detector.language.code
    else:
        return None


@app.route('/entity_extraction', methods=['POST'])
def get_entities():
    if not request.json or 'text' not in request.json:
        abort(400)
    text = request.json['text']
    if 'lan' in request.json:
        lan = request.json['lan']
    else:
        lan = get_language(text[:2500])
    if lan == 'en':
        doc = nlp_en(text)
        method = 'spacy_english'
        ents = [{'text': ent.text, 'start': ent.start_char,
                'end': ent.end_char, 'label': ent.label_}
                for ent in doc.ents]
    elif lan in supported_ner_spacy:
        method = 'spacy_multilingual'
        doc = nlp(text)
        ents = [{'text': ent.text, 'start': ent.start_char,
                'end': ent.end_char, 'label': ent.label_}
                for ent in doc.ents]
    elif lan in supported_ner_polyglot:
        method = 'polyglot'
        poly_text = Text(text, hint_language_code=lan)
        ents = []
        spans = []
        # Each entity is only once inside the list and then matched.
        # This is done because Polyglot only knows words, not char indices.
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
    else:
        method = 'not supported'
        ents = []
    response = {'language': lan, 'method': method, 'entities': ents}
    return jsonify(response), 200


@app.route('/language_detection', methods=['POST'])
def return_language():
    if not request.json or 'text' not in request.json:
        abort(400)
    language = get_language(request.json['text'])
    return jsonify({'language': language}), 200


if __name__ == "__main__":
    if len(sys.argv) == 2:
        POLY_PATH = sys.argv[1]
    elif len(sys.argv) > 2:
        print(f'unknown argument(s) {sys.argv[2:]}')
        exit(-1)
    supported_ner_polyglot = [name for name in os.listdir(POLY_PATH)]
    app.run()
