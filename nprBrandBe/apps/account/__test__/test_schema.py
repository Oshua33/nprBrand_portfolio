from nprOlusolaBe.apps.account.v1 import schemas


def test_create_user_schema():
    testing_data = dict(
        email="test@example.com",
        password="password123",
        first_name="John",
        last_name="Doe",
    )
    schema = schemas.UserRegistration(**testing_data)
    assert schema.email == testing_data.get("email")
    assert schema.password == testing_data.get("password")
    assert schema.first_name == testing_data.get("first_name")
    assert schema.last_name == testing_data.get("last_name")
    passed_data = schema.model_dump()
    for key, _ in passed_data.items():
        assert testing_data.get(key) == testing_data.get(key)
