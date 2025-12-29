from nprOlusolaBe.apps.news_letter.models import NewsLetter


def test_create_news_letter_model():
    testing_data = dict(
        email="test2@example.com",
    )
    new_contact = NewsLetter(
        email=testing_data.get("email")
    )

    assert new_contact.email == testing_data.get("email")
    
