import mongomock
import pymongo
import pytest

@pytest.fixture
def client():
    client = mongomock.MongoClient()
    db = client.cod
    challenge_collection = db['challenge']

    challenge_collection.create_index([
        ('image_name', pymongo.ASCENDING),
        ('image_ver', pymongo.DESCENDING)
    ], unique=True)

    challenge_collection.insert_one({
        "_id": "6524bec1adb7238a3c812a8b",
        "email": "cs302@smu.com",
        "image_name": "first_challenge",
        "image_ver": "1.0"
    })

    return challenge_collection
