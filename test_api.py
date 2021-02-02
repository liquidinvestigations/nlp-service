from urllib.parse import urljoin
import requests

NLP_URL = 'http://127.0.0.1:5001/'

def call_nlp_server(endpoint, data_dict):
    url = urljoin(NLP_URL, endpoint)
    resp = requests.post(url, json=data_dict)
    if (resp.status_code != 200
            or resp.headers['Content-Type'] != 'application/json'):
        raise RuntimeError(f"Unexpected response from nlp service: {resp}")
    return resp

def get_entities_from_service(text, language='en'):
    data = {'text': text}
    if language:
        data['language']= language
    resp = call_nlp_server('entity_extraction', data)
    entity_list = resp.json()
    return entity_list
