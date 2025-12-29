from esmerald.testclient import EsmeraldTestClient
from esmerald import status





def test_create_user_duplicate(client: EsmeraldTestClient, user_payload):
    response = client.post("/users", json=user_payload)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["data"] == "Account was created successfully, kindly check your email for email verification"
    response = client.post("/users", json=user_payload)
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"]["message"] == "User already exists"



def test_create_user(client: EsmeraldTestClient, get_new_account, user_payload):
    token_data = get_new_account
    for key, value in token_data.items():
        assert user_payload[key] == value
   

def test_create_admin(create_admin_user, admin_payload):
    token_data = create_admin_user
    for key, value in token_data.items():
        assert admin_payload[key] == value



def test_email_exist(client: EsmeraldTestClient, user_payload):
    client.post("/users/", json=user_payload)
    response = client.post("/users/", json=user_payload)
    assert response.status_code == 409
    res = response.json()
    assert res["detail"]["message"] == "User already exists"


# create a test for missing fields when regristing an admin
def test_admin_missing_fields(client: EsmeraldTestClient, incomplete_admin_payload):
    res = client.post("/users/admin", json=incomplete_admin_payload)
    assert res.status_code == status.HTTP_401_UNAUTHORIZED
    assert res.json()["detail"] == "You do not have authorization to perform this action."
        
  
