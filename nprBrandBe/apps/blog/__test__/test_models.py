from nprOlusolaBe.apps.media.models import Media
from nprOlusolaBe.apps.blog.models import BlogCategory, Blog
from nprOlusolaBe.apps.label.models import Label

def test_create_blog_model():
    # Provide all required fields for Media
    test_image = Media(
        url="http://example.com/test_image.png",
        type="image/png",
        file_name="test_image.png"
    )


    # Provide all required fields for BlogCategory
    test_category = BlogCategory(name="Test Category")
    

    # Provide all required fields for Label
    test_label = Label(
        title="Test Label Title",
        type="Test Type"
    )


    # Create Blog instance
    new_blog = Blog(
        title="test title",
        description="test content",
        image=test_image,
        is_publish=True,
        category=test_category,
        label=test_label
    )


    assert new_blog.title == "test title"
    assert new_blog.image == test_image

