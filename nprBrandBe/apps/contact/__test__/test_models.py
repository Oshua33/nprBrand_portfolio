import pytest
from nprOlusolaBe.apps.contact.models import Contact

@pytest.mark.asyncio
async def test_create_contact_model():
    testing_data = dict(
        email="test2@example.com",
        content="test content",
        name="John",
        company="Doe",
    )
    new_contact = await Contact.query.create(
        email=testing_data.get("email"),
        content=testing_data.get("content"),
        name=testing_data.get("name"),
        company=testing_data.get("company"),
    
    )
    assert new_contact.id != None
    assert new_contact.email == testing_data.get("email")
    assert new_contact.content == testing_data.get("content")
    assert new_contact.name == testing_data.get("name")
    assert new_contact.company == testing_data.get("company")
