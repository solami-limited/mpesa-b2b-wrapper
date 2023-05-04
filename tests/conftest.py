import os
import pytest
from src import create_app


@pytest.fixture(scope="session")
def app():
    app = create_app('testing')
    yield app


@pytest.fixture(scope="session")
def client(app):
    return app.test_client()


@pytest.fixture(scope="session")
def runner(app):
    return app.test_cli_runner()


@pytest.fixture(scope="session")
def supply_test_config():
    """Supply the test configuration to the app."""
    config = {**os.environ}
    return config
