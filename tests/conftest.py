import pytest

from app import get_app


@pytest.fixture
def app():
    app = get_app()
    return app


def pytest_addoption(parser):
    parser.addoption(
        "--hostname",
        action="store",
        default='http://127.0.0.1:5000/'
    )


@pytest.fixture()
def hostname(request):
    return request.config.getoption("--hostname")
