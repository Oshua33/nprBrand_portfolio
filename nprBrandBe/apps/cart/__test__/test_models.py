from decimal import Decimal
from nprOlusolaBe.apps.cart.models import Cart
from nprOlusolaBe.apps.account.models import User
from nprOlusolaBe.apps.product.models import Product, ProductStatus
from nprOlusolaBe.apps.media.models import Media  # Assuming Media model exists

def test_create_cart_model():
    # Create test user
    test_user = User(
        username="test_user",
        first_name="Test",
        last_name="User",
        email="test_user@example.com",
        password="securepassword123"
    )
   

    # Create test image for the product (optional)
    test_image = Media(
        url="http://example.com/test_product_image.png",
        type="image/png",
        file_name="test_product_image.png"
    )
 

    # Create test product with all required fields
    test_product = Product(
        name="Test Product",
        content="This is a test product.",
        price=Decimal("10.99"),
        image=test_image,                 # Optional field
        quantity=100,
        status=ProductStatus.IN_STOCK    # Assuming ProductStatus enum
    )
    

    # Create Cart instance
    new_cart = Cart(
        user=test_user,
        product=test_product,
        quantity=2
    )
    

    # Assertions to verify the cart was created correctly
    assert new_cart.user == test_user
    assert new_cart.product == test_product
    assert new_cart.quantity == 2
