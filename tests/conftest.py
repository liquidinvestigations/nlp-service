import pytest

from app import get_app


@pytest.fixture
def app():
    app = get_app()
    return app

