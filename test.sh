#!/bin/bash -ex
export NLP_SERVICE_MODELS_JSON='{"spacy":["xx_ent_wiki_sm", "en_core_web_sm"],"polyglot":["en", "de", "ro"]}'
drone exec --event push --pipeline static-tests .drone.yml
drone exec --event push --pipeline integration-test .drone.yml
