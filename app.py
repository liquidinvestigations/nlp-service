import os
from numpy.core.function_base import add_newdoc
import spacy
import re
from polyglot.text import Text
from polyglot.detect import Detector
from flask import Flask, request, jsonify, abort
nlp = spacy.load('xx_ent_wiki_sm')
nlp_en = spacy.load('en_core_web_sm')
supported_ner_polyglot = [name for name in os.listdir("/root/polyglot_data/ner2")]
supported_ner_spacy = ['nl','en','fr','de','it','pl','pt','ru','es']

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
    if not request.json or not 'text' in request.json:
        abort(400)
    text = request.json['text']
    method = 'spacy'
    if 'lan' in request.json:
        if request.json['lan'] == 'en':
            doc = nlp_en(text)
        else:
            doc = nlp(text)
    else:
        lan = get_language(text[:2500])
        if lan == 'en':
            doc = nlp_en(text)
            ents = [{'text': ent.text, 'start': ent.start_char, 'end': ent.end_char, 'label': ent.label_} for ent in doc.ents]
        elif lan in supported_ner_spacy:
            doc = nlp(text)
            ents = [{'text': ent.text, 'start': ent.start_char, 'end': ent.end_char, 'label': ent.label_} for ent in doc.ents]
        elif lan in supported_ner_polyglot:
            method = 'polyglot'
            poly_text = Text(text, hint_language_code=lan)
            ents = []
            entity_text = list(set([(' '.join(entity),entity.tag.lstrip('I-')) for entity in poly_text.entities]))
            for entity in entity_text:
                for match in re.finditer(entity[0], text):
                    ents.append({'text': entity[0], 'start': match.start(), 'end': match.end(), 'label': entity[1]})
        else:
            return 'language is not supported', 501
        response = {'language': lan, 'method':method, 'entities': ents}
        return jsonify(response), 200
                    


if __name__ == "__main__":
    app.run()
