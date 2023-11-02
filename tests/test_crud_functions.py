import pytest
import sys
import os

os.chdir('/usr/image_builder/src')
sys.path.append('../tests')

from conftest import client
from config.crud_functions import CrudFunctions
from conftest import imageA, imageB

#############
# VARIABLES #
#############

imageC = {
    "_id": "6524bec1adb7238a3c812a8f",
    "corId": "cor6969",
    "creatorName": "cs302",
    "imageName": "third_image",
    "imageRegistryLink": "gitlab.com/third_image:1.0",
    "s3Path": "github.com/s3/bye",
}

#############
# UNIT TEST #
#############


def test_get_all_images_success(client):
    crud = CrudFunctions(client)
    result = crud.get_all_images()

    assert result["message"] == "Success"
    assert len(result["data"]) == 2


def test_get_image_by_ids_success(client):
    ids = {"corId": ["cor69"]}
    crud = CrudFunctions(client)
    result = crud.get_image_by_ids(ids)

    assert result["message"] == "Success"
    assert result["data"] == [imageA]


def test_get_image_by_ids_notfound(client):
    ids = {"corId": ["123"]}
    crud = CrudFunctions(client)
    result = crud.get_image_by_ids(ids)

    assert result["message"] == "Not Found"
    assert result["data"]["Not Found"] == ["123"]


def test_add_image_success(client):
    crud = CrudFunctions(client)
    result = crud.add_image(imageC)

    assert result["message"] == "Successfully created"
    assert result["data"] == imageC


def test_add_image_duplicated_name_ver(client):
    crud = CrudFunctions(client)
    result = crud.add_image(imageA)

    assert result["message"] == "Bad Request"
    assert result["data"] == "Image name and version is duplicated!"


def test_add_image_fail(client):
    crud = CrudFunctions(client)
    result = crud.add_image({})

    assert result["message"] == "Bad Request"
    assert result["data"] == "Request body cannot be empty and image body is required"


def test_update_image_by_id(client):
    body = imageA.copy()
    body["creatorName"] = "Jacky"
    body["imageName"] = "updated_image"
    crud = CrudFunctions(client)
    result = crud.update_image_by_id(body)

    expected = body.copy()

    assert result["message"] == "Success"
    assert result["data"] == expected


def test_update_image_by_id_no_id(client):
    body = imageA.copy()
    body.pop("corId")
    crud = CrudFunctions(client)
    result = crud.update_image_by_id(body)

    assert result["message"] == "Bad Request"
    assert result["data"] == "Request body and image ID is required"


def test_update_image_by_id_notfound(client):
    body = imageA.copy()
    body["corId"] = "hi"
    crud = CrudFunctions(client)
    result = crud.update_image_by_id(body)

    assert result["message"] == "Not Found"
    assert result["data"] == "Image not found"


def test_delete_images_by_id_success(client):
    body = {"corId": ["cor69", "cor123"]}
    crud = CrudFunctions(client)
    crud.add_image(imageC)
    result = crud.delete_images_by_ids(body)

    assert result["message"] == "Success"
    assert len(result["data"]) == len(body["corId"])


def test_delete_images_by_id_invalidCorId(client):
    body = {"corId": ["cor29109", "sdosj"]}
    crud = CrudFunctions(client)
    crud.add_image(imageC)
    result = crud.delete_images_by_ids(body)

    assert result["message"] == "Internal Server Error"
    assert result["data"] == "Unable to delete records"


def test_delete_all_images_Success(client):
    crud = CrudFunctions(client)
    result = crud.delete_all_images()

    assert result["message"] == "Success"
    assert result["data"] == [imageA, imageB]
    assert 0 == len(crud.get_all_images()["data"])