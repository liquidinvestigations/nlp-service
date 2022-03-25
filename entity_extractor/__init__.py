from flask import Flask
import os

app = Flask(__name__)

app.config['JSON_SORT_KEYS'] = False
app.config['SPACY_MULTILINGUAL_LAN_CODE'] = 'xx'
app.config['SPACY_MULILINGUAL_LANGUAGES'] = ['nl', 'en', 'fr', 'de', 'it', 'pl', 'pt', 'ru', 'es']

app.config['FALLBACK_LANGUAGE'] = os.getenv('NLP_SERVICE_FALLBACK_LANGUAGE')
app.config['SPACY_TEXT_LIMIT'] = int(os.getenv('NLP_SPACY_TEXT_LIMIT', default=100000))


def get_app():
    """returns the app for testing.

    Returns:
        the app, for testing.
    """
    return app


if __name__ == "__main__":
    app.run()

import entity_extractor.views.nlp_entities
import entity_extractor.views.regex_entities
