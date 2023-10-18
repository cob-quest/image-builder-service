import pytest
from src import crud_functions

@pytest.mark.dependency()
def test_get_all_challenges(client):
    result = crud_functions.get_all_challenges(client)

    assert result['message'] == 'Success'
    assert result['data'] == {
        "6524bec1adb7238a3c812a8b": {
            "email": "cs302@smu.com",
            "image_name": "first_challenge",
            "image_ver": "1.0"
        }
    }
    

@pytest.mark.dependency(depends=['test_get_all_challenges'])
def test_get_challenge_by_ids(client):
    ids = {"_id": ["6524bec1adb7238a3c812a8b"]}
    result = crud_functions.get_challenge_by_ids(ids, client)

    assert result['message'] == 'Success'
    assert result['data'] == {
        "6524bec1adb7238a3c812a8b": {
            "email": "cs302@smu.com",
            "image_name": "first_challenge",
            "image_ver": "1.0"
        }
    }


@pytest.mark.dependency(depends=['test_get_all_challenges'])
def test_add_challenge_success(client):
    result = crud_functions.add_challenge({
        "_id": "6524c308d74b9e961ddcdb1a", 
        "email": "cs302@google.com",
        "image_name": "another_challenge",
        "image_ver": "1.0"}, client)
    
    assert result['message'] == "Successfully created"
    assert result['data'] == {
        "_id": "6524c308d74b9e961ddcdb1a",
        "email": "cs302@google.com",
        "image_name": "another_challenge",
        "image_ver": "1.0"
    }


@pytest.mark.dependency(depends=['test_get_all_challenges', 'test_add_challenge_success'])
def test_add_challenge_duplicated_name_ver(client):
    result = crud_functions.add_challenge({
        "_id": "6524c308d74b9e961ddcdb1a", 
        "email": "cs302@smu.com",
        "image_name": "first_challenge",
        "image_ver": "1.0"}, client)
    
    assert result['message'] == "Bad Request"
    assert result['data'] == "Image name and version is duplicated!"


@pytest.mark.dependency(depends=['test_get_all_challenges'])
def test_add_challenge_fail(client):
    result = crud_functions.add_challenge({}, client)
    

    assert result['message'] == 'Bad Request'
    assert result['data'] ==  "Request body cannot be empty and challenge body is required"


@pytest.mark.dependency(depends=['test_get_all_challenges', 'test_get_challenge_by_ids'])
def test_get_challenge_by_ids_notfound(client):
    ids = {"_id": ["123"]}
    result = crud_functions.get_challenge_by_ids(ids, client)

    assert result['message'] == 'Not Found'
    assert result['data']['Not Found'] == ["123"]


@pytest.mark.dependency(depends=["test_get_all_challenges"])
def test_update_challenge_by_id(client):
    body = {
        "_id": "6524bec1adb7238a3c812a8b",
        "email": "cs302@xmail.com",
        "image_name": "updated_image",
        "image_ver": "1.0"
    }
    
    result = crud_functions.update_challenge_by_id(body, client)

    assert result['message'] == "Success"
    assert result['data'] == {
        "email": "cs302@xmail.com",
        "image_name": "updated_image",
        "image_ver": "1.0"
    }


@pytest.mark.dependency(depends=["test_get_all_challenges", "test_update_challenge_by_id"])
def test_update_challenge_by_id_no_id(client):
    body = {
        "email": "cs302@xmail.com",
        "image_name": "updated_image",
        "image_ver": "1.0"
    }
    
    result = crud_functions.update_challenge_by_id(body, client)

    assert result['message'] == "Bad Request"
    assert result['data'] == "Request body and challenge ID is required"


@pytest.mark.dependency(depends=["test_get_all_challenges", "test_update_challenge_by_id", "test_update_challenge_by_id_no_id"])
def test_update_challenge_by_id_notfound(client):
    body = {
        "_id": "6524c308d74b9e961ddcdb1a",
        "email": "cs302@xmail.com",
        "image_name": "updated_image",
        "image_ver": "1.0"
    }
    
    result = crud_functions.update_challenge_by_id(body, client)

    assert result['message'] == "Not Found"
    assert result['data'] == "Challenge not found"
