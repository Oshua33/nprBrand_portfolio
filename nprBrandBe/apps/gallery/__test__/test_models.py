from decimal import Decimal

import pytest
from nprOlusolaBe.apps.gallery.models import Gallery
from nprOlusolaBe.apps.media.models import Media
from nprOlusolaBe.apps.label.models import Label  


@pytest.mark.asyncio
async def test_create_gallery_model():

    test_label = await Label.query.create(
        title="Test Label Title",
        type="Test Type"
    )


    # Create test image for the product (optional)
    test_image = await Media.query.create(
        url="http://example.com/test_product_image.png",
        type="image/png",
        file_name="test_product_image.png"
    )
    assert test_image.id != None
    assert test_image.url == "http://example.com/test_product_image.png"
    assert test_image.type == "image/png"
    assert test_image.file_name == "test_product_image.png"


    new_gallery = await Gallery.query.create(
        title="test_title",
        label=test_label,
        image=test_image
    )
    assert new_gallery.id != None
    assert new_gallery.title == "test_title"
    assert new_gallery.label.id == test_label.id
    assert new_gallery.image.id == test_image.id

    assert new_gallery.id!= None
    assert new_gallery.title == "test_title"
    assert new_gallery.label.id  == test_label.id
    assert new_gallery.image.id == test_image.id
