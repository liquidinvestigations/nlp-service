from urllib.parse import urljoin
import requests
import pytest

NLP_URL = 'http://127.0.0.1:5001/'

# test cases are tuples consisting of (text, language code, method used, number of found entities)
test_cases = [
    ("""(A) “Skont l-Artikolu 4(2)(a) tal-Kodiċi ta' Kondotta, qiegħed niddikjara l-attività/ajiet professjonali
    tiegħi matul it-tliet snin qabel il-ħatra tiegħi fil-Parlament, u il-parteċipazzjoni tiegħi matul dak il-
    perjodu f'kumitati jew bordijiet ta' kumpaniji, organizzazzjonijiet mhux governattivi, assoċjazzjonijiet
    jew kwalunkwe organu ieħor stabbilit fil-liġi:”""", 'mt', 'not supported', 0),
    ("""(A) "Pursuant to Article 4(2)(a) of the Code of Conduct I declare my occupation(s) during the
    three-year period before I took up office with the Parliament, and membership during that period
    of any boards or committees of companies, non-governmental organisations, associations or other
    bodies established in law:""", 'en', 'spacy_english', 3),
    ("""CÓD IOMPAIR D’FHEISIRÍ PHARLAIMINT NA HEORPA MAIDIR LE LEASANNA AIRGEADAIS AGUS COINBHLEACHTAÍ LEASA
    A BHEIDH LE TÍOLACADH DON UACHTARÁN FAOI DHEIREADH AN CHÉAD PHÁIRTSEISIÚIN TAR ÉIS NA TOGHCHÁIN
    DO PHARLAIMINT NA HEORPA A BHEITH ANN NÓ LAISTIGH DE 30 LÁ Ó DHUL I MBUN OIFIGE LEIS AN BPARLAIMINT""", 'ga', 'not supported', 0),
    ("""1 Gehen dem Präsidenten Informationen zu, die ihm Anlass zu der Annahme geben, dass die Erklärung über die finanziellen
    Interessen eines Mitglieds sachlich unzutreffend oder veraltet ist, kann er gemäß Artikel 4 Absatz 5 des Verhaltenskodex den
    nach Artikel 7 des Verhaltenskodex vorgesehenen Beratenden Ausschuss konsultieren; gegebenenfalls fordert er das Mitglied
    auf, die Erklärung innerhalb von zehn Tagen zu korrigieren. Das Präsidium kann einen Beschluss zur Anwendung von Artikel
    4 Absatz 4 des Verhaltenskodex auf Mitglieder annehmen, die der Aufforderung des Präsidenten zu einer Korrektur nicht
    nachkommen.
    2 Beispiel: Ergibt sich am 10. März eine Änderung, ist die entsprechend geänderte Erklärung über die finanziellen Interessen
    bis spätestens 30. April vorzulegen.
    3 Nur eine Berufstätigkeit/Mitgliedschaft während des Dreijahreszeitraums vor dem Beginn des Mandats in der laufenden
    Wahlperiode, einschließlich der Mitgliedschaft im Europäischen Parlament, sollte angegeben werden.
    4 Bei jedem zu meldenden Punkt gibt das Mitglied gegebenenfalls an, ob die Tätigkeit vergütet wird oder nicht; bei den
    Punkten a, c, d, e und f geben""", 'de', 'spacy_multilingual', 4),
    ("""1 În conformitate cu articolul 4 alineatul (5) din Codul de conduită, în cazul în care primește informații pe baza cărora
    consideră că declarația de interese financiare a unui deputat este substanțial incorectă sau nu mai este de actualitate,
    Președintele poate consulta Comitetul consultativ prevăzut la articolul 7 din Codul de conduită și, după caz, îi solicită
    deputatului să corecteze declarația în termen de 10 zile. Biroul poate adopta o decizie de aplicare a articolului 4 alineatul (4)
    din Codul de conduită în cazul deputaților care nu dau curs solicitării de corectare adresate de Președinte.
    2 Exemplu: dacă survine o schimbare la 10 martie, declarația privind interesele financiare modificată în consecință este
    înaintată până la data de 30 aprilie, cel târziu.
    3 Trebuie declarate numai activitățile profesionale desfășurate sau calitatea de membru deținută în ultimii trei ani înainte de
    începerea mandatului în legislatura actuală, inclusiv calitatea de deputat în Parlamentul European.
    4 Pentru fiecare dintre elementele declarate, deputații indică, atunci când este cazul, dacă au fost sau nu remunerate; pentru
    elementele (a), (c), (d), (e) și (f), deputații indică și una dintre următoarele categorii de venit:""", 'ro', 'polyglot', 3)
        ]


def call_nlp_server(endpoint, data_dict):
    url = urljoin(NLP_URL, endpoint)
    resp = requests.post(url, json=data_dict)
    if (resp.status_code != 200
            or resp.headers['Content-Type'] != 'application/json'):
        raise RuntimeError(f'Unexpected response from nlp service: {resp.content}')
    return resp


def get_language(text):
    data = {'text': text}
    resp = call_nlp_server('language_detection', data)
    language = resp.json()['language']
    return language


def extract_enitities(text, text_source, digest):
    # TODO: Add entity Extraction setting to snoop settings
    nlp_response = get_entities(text)
    ents = nlp_response['entities']
    results = {}
    results['lang'] = nlp_response['language']
    results['entities'] = [k['text'] for k in ents]
    unique_ents = set([(k['text'], k['type']) for k in ents])
    for entity_type in set(v['type'] for v in results['entities']):
        results[f'entity-type.{entity_type}'] = [k[0] for k in unique_ents
                                                 if k[1] == entity_type]
    text = text[:2500]
    results['lang'] = get_language(text[:2500])
    return results


def get_entities_from_service(text, language=None):
    data = {'text': text}
    if language:
        data['language'] = language
    resp = call_nlp_server('entity_extraction', data)
    entity_list = resp.json()
    return entity_list


def test_spacy_language():
    for case in test_cases:
        assert get_language(case[0][:2500]) == case[1]


def test_entity_extraction():
    for case in test_cases:
        response = get_entities_from_service(case[0])
        assert response['language'] == case[1]
        assert response['method'] == case[2]
        assert len(response['entities']) == case[3]

