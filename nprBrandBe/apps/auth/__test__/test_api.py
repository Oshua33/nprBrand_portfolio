from esmerald.testclient import EsmeraldTestClient
from esmerald import status




def test_login_account_not_found(client: EsmeraldTestClient, user_payload):
    response = client.post("/auths/login/", json=user_payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    

def test_user_login(get_user_login_token ):
    assert get_user_login_token['access_token'] != None
    assert get_user_login_token['refresh_token']!= None
    assert get_user_login_token['token_type'] == 'Bearer'

def test_admin_login(get_admin_login_token ):
    assert get_admin_login_token['access_token'] != None
    assert get_admin_login_token['refresh_token']!= None
    assert get_admin_login_token['token_type'] == 'Bearer'
  
    
