import pytest
from tests.conftest import client
from src.db import crud_functions


@pytest.mark.dependency()
def test_get_all_challenges(client):
    crud = crud_functions.CrudFunctions(client)
    result = crud.get_all_challenges()

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
    crud = crud_functions.CrudFunctions(client)
    result = crud.get_challenge_by_ids(ids)

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
     crud = crud_functions.CrudFunctions(client)
     result = crud.add_challenge({
         "_id": "6524c308d74b9e961ddcdb1a", 
         "email": "cs302@google.com",
         "image_name": "another_challenge",
         "image_ver": "1.0"})

     assert result['message'] == "Successfully created"
     assert result['data'] == {
         "_id": "6524c308d74b9e961ddcdb1a",
         "email": "cs302@google.com",
         "image_name": "another_challenge",
         "image_ver": "1.0"
     }


@pytest.mark.dependency(depends=['test_get_all_challenges', 'test_add_challenge_success'])
def test_add_challenge_duplicated_name_ver(client):
     crud = crud_functions.CrudFunctions(client)
     result = crud.add_challenge({
         "_id": "6524c308d74b9e961ddcdb1a", 
         "email": "cs302@smu.com",
         "image_name": "first_challenge",
         "image_ver": "1.0"})

     assert result['message'] == "Bad Request"
     assert result['data'] == "Image name and version is duplicated!"


@pytest.mark.dependency(depends=['test_get_all_challenges'])
def test_add_challenge_fail(client):
     crud = crud_functions.CrudFunctions(client)
     result = crud.add_challenge({})

     assert result['message'] == 'Bad Request'
     assert result['data'] ==  "Request body cannot be empty and challenge body is required"


@pytest.mark.dependency(depends=['test_get_all_challenges', 'test_get_challenge_by_ids'])
def test_get_challenge_by_ids_notfound(client):
     ids = {"_id": ["123"]}
     crud = crud_functions.CrudFunctions(client)
     result = crud.get_challenge_by_ids(ids)

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
     crud = crud_functions.CrudFunctions(client)
     result = crud.update_challenge_by_id(body)

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
     crud = crud_functions.CrudFunctions(client)
     result = crud.update_challenge_by_id(body)

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
     crud = crud_functions.CrudFunctions(client)
     result = crud.update_challenge_by_id(body)

     assert result['message'] == "Not Found"
     assert result['data'] == "Challenge not found"
