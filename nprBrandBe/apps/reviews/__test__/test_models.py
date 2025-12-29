from nprOlusolaBe.apps.reviews.models import Review
from nprOlusolaBe.apps.account.models import User

def test_create_reviews_model():
    test_user = User(
        username="test_user",
        first_name="Test",
        last_name="User",
        email="test_user@example.com",
        password="securepassword123"
    )
   
    
    testing_data = dict(
        name="Test name",
        email="test_user@example.com",
        content="test content",
        reviewer = test_user,
        is_accepted= True
    )
    
    new_review = Review(
        name=testing_data.get("name"),
        email=testing_data.get("email"),
        content=testing_data.get("content"),
        reviewer=testing_data.get("reviewer"),
        is_accepted=testing_data.get("is_accepted")
        
    )

    assert new_review.name == testing_data.get("name")
    assert new_review.email == testing_data.get("email")
    assert new_review.content == testing_data.get("content")
    assert new_review.reviewer == testing_data.get("reviewer")
    assert new_review.is_accepted == testing_data.get("is_accepted")
    
    
    

