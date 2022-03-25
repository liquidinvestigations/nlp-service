import pytest
import sys
import os

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

from entity_extractor import get_app


@pytest.fixture
def app():
    app = get_app()
    return app
