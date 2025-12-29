from nprOlusolaBe.apps.auth.v1 import schemas


def test_create_login_schema(user_payload):
    schema = schemas.LoginIn(**user_payload)
    assert schema.email == user_payload.get("email")
    assert schema.password == user_payload.get("password")

    passed_data = schema.model_dump()
    for key, _ in passed_data.items():
        assert user_payload.get(key) == user_payload.get(key)
