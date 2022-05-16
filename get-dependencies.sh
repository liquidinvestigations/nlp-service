#!/bin/bash -e

SPACY_VERSION=v3.0.5
curl -s https://raw.githubusercontent.com/explosion/spaCy/$SPACY_VERSION/website/meta/languages.json > langs.json

echo DEPENDENCIES:
cat langs.json| jq '.languages[] | {dependencies}[] | .' | grep name | sort -u | cut -d':' -f2 | tr -d ' ,"' | tee extra-requirements.txt
echo
