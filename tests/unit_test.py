import pytest
import app
import json

# test cases are tuples consisting of (text, language code, model used, number of found entities)
with open('tests/data/test_cases.json', 'r') as f:
    test_cases = json.loads(f.read())


@pytest.fixture
def client():
    app.app.config['TESTING'] = True
    return lambda endpoint, data, model='': call_nlp_server(app.get_app().test_client(),
                                                            endpoint, data, model)


def call_nlp_server(client, endpoint, text, model=''):
    if endpoint == "/config":
        resp = client.get(f'{endpoint}')
    else:
        data = {'text': text}
        if model:
            data['model'] = model
        resp = client.post(f'{endpoint}', json=data)
    if (resp.status_code not in [200, 500] or resp.headers['Content-Type'] != 'application/json'):
        raise RuntimeError(f'Unexpected response from nlp service: {resp.data}')
    return resp.get_json()


def test_spacy_language(client):
    for case in test_cases['no errors']:
        assert client("/language_detection", case['text'])["language"] == case['expected_language']


def test_entity_extraction(client):
    for case in test_cases['no errors']:
        model = case['used model'] if 'used model' in case else ''
        response = client('/entity_extraction', case['text'], model)
        print(response)
        assert response['language'] == case['expected_language']
        assert response['model'] == case['expected_model']
        assert len(response['entities']) == case['expected_entities']


def test_error_responses(client):
    for case in test_cases['errors']:
        model = case['used model'] if 'used model' in case else ''
        response = client('/entity_extraction', case['text'], model)
        assert response['error'] == case['expected_error']


def test_config_endpoint(client):
    test_conf = {"spacy": ["xx_ent_wiki_sm", "en_core_web_sm"],
                 "polyglot": ["en", "de", "ro"]
                 }
    assert client("/config", None) == test_conf
