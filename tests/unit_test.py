import pytest
import app
import json

# test cases are tuples consisting of (text, language code, method used, number of found entities)
with open('tests/data/test_cases.json', 'r') as f:
    test_cases = json.loads(f.read())


@pytest.fixture
def client():
    app.app.config['TESTING'] = True
    return lambda endpoint, data: call_nlp_server(app.get_app().test_client(), endpoint, data)


def call_nlp_server(client, endpoint, text):
    data = {'text': text}
    resp = client.post(f'{endpoint}', json=data)
    if (resp.status_code != 200
            or resp.headers['Content-Type'] != 'application/json'):
        raise RuntimeError(f'Unexpected response from nlp service: {resp.data}')
    return resp.get_json()


def test_spacy_language(client):
    for case in test_cases:
        assert client("/language_detection", case['text'])["language"] == case['expected_language']


def test_entity_extraction(client):
    for case in test_cases:
        response = client('/entity_extraction', case['text'])
        assert response['language'] == case['expected_language']
        assert response['method'] == case['expected_method']
        assert len(response['entities']) == case['expected_entities']
