import os
import pytest
from esmerald.testclient import EsmeraldTestClient
from nprOlusolaBe.apps.account.models import User
from nprOlusolaBe.apps.account.service import AccountService
from nprOlusolaBe.apps.account.v1.schemas import UserAdminRegistration
from nprOlusolaBe.core.service import BaseService
from nprOlusolaBe.lib.database.connection import get_db_connection
from nprOlusolaBe.main import get_application
from esmerald import status


def create_app():
    os.environ.setdefault("ENVIRONMENT", "testing")
    app = get_application()
    app.settings.environment = "testing"
    return app


registry = get_db_connection()


pytestmark = pytest.mark.anyio


def get_client():
    return EsmeraldTestClient(
        create_app(),
        backend="asyncio",
        raise_server_exceptions=False,
        base_url="http://testserver/api/v1",
    )


@pytest.fixture
def client():
    yield get_client()


@pytest.fixture(autouse=True, scope="function")
async def create_test_database():
    await registry.create_all()
    yield
    await registry.drop_all()


@pytest.fixture(autouse=True)
async def rollback_transactions():
    with registry.database.force_rollback():
        async with registry.database:
            yield

@pytest.fixture
def user_payload():
    return {
        "email": "test_user@example.com",
        "password": "secure_password",
        "first_name": "New",
        "last_name": "User",
    }
    




@pytest.fixture
def user_payload():
    return {
        "email": "test_user@example.com",
        "password": "secure_password",
        "first_name": "New",
        "last_name": "User",
    }


@pytest.fixture
def admin_payload():
    return {
        "email": "test_admin@example.com",
        "password": "secure_password",
        "first_name": "New",
        "last_name": "User",
        "is_staff": True,
        "is_superuser": True,
    }


@pytest.fixture
def incomplete_admin_payload():
    return {
        "email": "test_admin@example.com",
        "password": "secure_password",
        "first_name": "New",
        "last_name": "User",
        "is_superuser": True,
    }


@pytest.fixture
async def create_admin_user(admin_payload):
    service = AccountService()
    response = await service.create_special_user(
        UserAdminRegistration(
            **admin_payload
        )
    )
    response.status_code = 201
    return admin_payload

@pytest.fixture
def get_new_account(user_payload, client):
    response = client.post("/users", json=user_payload)
    assert response.status_code == 201
    assert response.json()["data"] == "Account was created successfully, kindly check your email for email verification"
    return user_payload

@pytest.fixture
def get_user_login_token(client: EsmeraldTestClient, get_new_account ):
    user_data = get_new_account
    response = client.post("/auths/login/", json=user_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['access_token'] != None
    assert data['refresh_token']!= None
    assert data['token_type'] == 'Bearer'
    return response.json()

@pytest.fixture
def get_admin_login_token(client: EsmeraldTestClient, create_admin_user ):
    response = client.post("/auths/login/", json=create_admin_user)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['access_token'] != None
    assert data['refresh_token']!= None
    assert data['token_type'] == 'Bearer'
    return response.json()