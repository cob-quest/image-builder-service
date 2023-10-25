import mongomock
import pymongo
import pytest

imageA = {
    "_id": "6524bec1adb7238a3c812a8b",
    "corId": "cor69",
    "creatorName": "cs302",
    "imageName": "second_image",
    "imageRegistryLink": "gitlab.com/first_image:1.0",
    "s3Path": "github.com/s3/test",
}

imageB = {
    "_id": "6524bec1adb7238a3c812a8c",
    "corId": "cor123",
    "creatorName": "cs302",
    "imageName": "first_image",
    "imageRegistryLink": "gitlab.com/first_image:1.0",
    "s3Path": "github.com/s3/hello",
}


@pytest.fixture
def client():
    client = mongomock.MongoClient()
    db = client.cod
    image_collection = db["image_builder"]

    image_collection.create_index([("corId", pymongo.ASCENDING)], unique=True)

    image_collection.insert_many([imageA, imageB])

    return image_collection
