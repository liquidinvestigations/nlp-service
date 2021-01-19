import spacy
from flask import Flask, request, jsonify, make_response, abort
nlp = spacy.load('xx_ent_wiki_sm')
nlp_en = spacy.load('en_core_web_sm')


app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False


@app.route('/entity_extraction', methods=['POST'])
def get_entities():
    if not request.json or not 'text' in request.json:
        abort(400)
    text = request.json['text']
    if 'lan' in request.json:
        if request.json['lan'] == 'en':
            doc = nlp_en(text)
        else:
            doc = nlp(text)
    ents = [{'text': ent.text, 'start': ent.start_char, 'end': ent.end_char, 'label': ent.label_} for ent in doc.ents]
    return jsonify(ents), 200


if __name__ == "__main__":
    app.run()
