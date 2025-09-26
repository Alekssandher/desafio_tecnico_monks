from http import HTTPStatus
from fastapi.testclient import TestClient
from api.api import app
import pytest

@pytest.fixture
def client():
    return TestClient(app)

def test_check_api_health_should_return_200_if_ok(client):
    
    res = client.get("/healthcheck")
    assert res.status_code == HTTPStatus.OK
    