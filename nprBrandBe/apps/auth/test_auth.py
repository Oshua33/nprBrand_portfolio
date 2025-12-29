# import json
# from pydoc import cli
# import pytest
# from nprOlusolaBe.apps.account.service import AccountService
# from nprOlusolaBe.apps.account.v1.schemas import UserRegistration
# from esmerald.testclient import EsmeraldTestClient
# from httpx import Response



# # pytestmark = pytest.mark.anyio


# @pytest.fixture
# def client():
#     from nprOlusolaBe.tests.test_app import get_client

#     return get_client()


# @pytest.fixture
# def user_payload():
#     return {
#         "email": "new_user@example.com",
#         "password": "secure_password",
#         "first_name": "New",
#         "last_name": "User",
#     }


# @pytest.fixture
# def admin_payload():
#     return {
#         "email": "new_user@example.com",
#         "password": "secure_password",
#         "first_name": "New",
#         "last_name": "User",
#         "is_staff": "False",
#         "is_superuser": "False",
#     }


# async def test_create_user():
#     response: Response = client.post("/users/", json=user_payload)

#     assert response.status_code == 201
#     # assert response.json()["email"] == user_payload["email"]


# async def test_create_special_user(
#     client: EsmeraldTestClient,
#     admin_payload,
# ):
#     response: Response = client.post("/users/admin", json=admin_payload)
#     assert response.status_code == 201




