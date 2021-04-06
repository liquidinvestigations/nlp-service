""" Downloader for language models used for Named Entity Recognition. The models
which should be downloaded must be stored in an environment variable
NLP_SERVICE_MODELS_JSON. The environment variable NLP_SERVICE_MODELS_JSON is a
json formatted string containing all models to be downloaded in two keys 'spacy'
and 'polyglot', followed by a list of model names for spacy (since there are
many models per language) and languages for polyglot. For Polyglot, both the
embeddings and the NER models are downloaded, as both are needed for NER. The
allowed spacy models are listed here, because spacy does not provide a proper
infrastructure for automatically downloading models via script. It is is easier
to just assert that the language models are properly named before attempting to
download, as the download script of spacy automatically exists and doesn't throw
an exception.
"""

import os
import shutil
import logging
import json
import spacy
import argparse
from polyglot.downloader import downloader

ALLOWED_POLY_LANGUAGES = ['en', 'de', 'ar', 'bg', 'ca', 'cs', 'da',  'el', 'et', 'fa',
                          'fi', 'he', 'hi', 'hr', 'hu', 'id', 'ja', 'ko', 'lt', 'lv',
                          'ms', 'no', 'ro', 'sk', 'sl', 'sr', 'sv', 'th', 'tl', 'tr',
                          'uk', 'vi', 'zh']

ALLOWED_SPACY_MODELS = ['zh_core_web', 'da_core_news', 'nl_core_news', 'en_core_web',
                        'fr_core_news' 'de_core_news', 'el_core_news', 'it_core_news',
                        'ja_core_news', 'lt_core_news', 'xx_ent_wiki', 'nb_core_news',
                        'pl_core_news', 'pt_core_news', 'ro_core_news', 'ru_core_news',
                        'es_core_news'
                        ]
ALLOWED_SPACY_MODEL_TYPES = ['sm', 'md', 'lg']


download_dir = '/data'

spacy_download_path = 'https://github.com/explosion/spacy-models/releases'


def download_models(donwloads):
    poly_downloads = []
    for language in donwloads['polyglot']:
        assert language in ALLOWED_POLY_LANGUAGES
        if not os.path.isdir(f'{download_dir}/polyglot_data/embeddings2/{language}'):
            poly_downloads.append(f'embeddings2.{language}')
            poly_downloads.append(f'ner2.{language}')
        else:
            logging.info(f'skipping {language}, already installed')
    if poly_downloads:
        downloader.download(poly_downloads,  download_dir=f'{download_dir}/polyglot_data')

    for model in donwloads['spacy']:
        if not spacy.util.is_package(model):
            logging.info(f'downloading spacy model {model}')
            model_name, type = model.rsplit('_', 1)
            assert model_name in ALLOWED_SPACY_MODELS
            assert type in ALLOWED_SPACY_MODEL_TYPES
            spacy.cli.download(model, False, False, '-t', '/data/spacy/', '--no-deps')
        else:
            logging.info(f'{model} is already installed')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--update', action='store_true')
    args = parser.parse_args()
    if args.update:
        logging.warn('downloading all models anew.')
        shutil.rmtree(download_dir)
        os.mkdir(download_dir)
    logging.info('downloading models from environment variable.')
    donwloads = json.loads(os.getenv('NLP_SERVICE_MODELS_JSON'))
    if donwloads:
        download_models(donwloads)
    else:
        logging.error('Environment variable NLP_SERVICE_MODELS_JSON is not defined')
        exit(1)
