from nprOlusolaBe.apps.account.models import User


def test_create_user_model():
    testing_data = dict(
        email="test2@example.com",
        password="password123",
        first_name="John",
        last_name="Doe",
    )
    new_user = User(
        email=testing_data.get("email"),
        password=testing_data.get("password"),
        first_name=testing_data.get("first_name"),
        last_name=testing_data.get("last_name"),
    )

    assert new_user.email == testing_data.get("email")
    assert new_user.password == testing_data.get("password")
    assert new_user.first_name == testing_data.get("first_name")
    assert new_user.last_name == testing_data.get("last_name")
