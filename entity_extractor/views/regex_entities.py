import logging
import re

from entity_extractor import app
from flask import abort, jsonify, request

log = logging.getLogger(__name__)

PHONE_NUMBER_RE = r'(?:(?:\(?(?:00|\+)([1-4]\d\d|[1-9]\d+)\)?)[\-\.\ \\\/]?)?((?:\(?\d{1,}\)?[\-\.\ \\\/]?){0,})(?:[\-\.\ \\\/]?(?:#|ext\.?|extension|x)[\-\.\ \\\/]?(\d+))?'  # noqa: E501


def get_phonenumbers(text):
    matches = re.finditer(PHONE_NUMBER_RE, text, re.MULTILINE)
    ents = []
    for match in matches:
        if match.group(0):
            ents.append({'text': match.group(0), 'start': match.start(), 'end': match.end(),
                         'type': 'phonenumber'})
    return ents


@app.route('/regex_entity_extraction', methods=['POST'])
def get_regex_entities():
    if not request.json or 'text' not in request.json:
        log.warning('POST /regex_entity_extraction 400')
        abort(400)
    text = request.json['text']

    ents = get_phonenumbers(text)

    return jsonify({'language': None, 'model': 'regex', 'entities': ents})
