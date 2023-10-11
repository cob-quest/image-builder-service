from models.Challenge import Challenge
from models.Response import Response
import db.db_connection as db_connection
from pymongo import errors
import testing.test_crud as test

def get_all_challenges():
    """Get all challenges

    Returns:
        JSON: JSON objects for all the challenges that are created
    """
    challenge_collection = db_connection.get_db_collection()

    records = challenge_collection.find()
    
    res = {}
    for record in records:
        id = record.pop('_id')
        res[id] = record
        
    if records:
        return Response("Success", res).to_dict()
    else:
        return Response("Internal Server Error", "Unable to read data").to_dict()


def get_challenge_by_ids(data={}):
    """Get challenges by the IDs provided.

    Args:
        data (dict, optional): A dict object that consists of a key of '_id' and a list of IDs. Defaults to {}.

    Returns:
        JSON: JSON objects for all the challenges that are found.
    """
    if not data:
        return Response("Bad Request", "Request body cannot be empty and challenges IDs are required").to_dict()
    
    ids = data.get("_id")
    
    if not ids:
        return Response("Bad Request", "A list of challenge IDs required").to_dict()

    challenge_collection = db_connection.get_db_collection()

    challenges = challenge_collection.find({"_id": {'$in': ids}})

    res = {}
    for challenge in challenges:
        challenge_id = challenge.pop("_id")
        res[challenge_id] = challenge
    
    if len(res) == len(ids):
        return Response("Success", res).to_dict()
    else:
        not_found = [id for id in ids if id not in res]
        return Response("Not Found", { "Found": res, "Not Found": not_found }).to_dict()


def add_challenge(data={}):
    """ Add a challenge into the database

    Returns:
        JSON: JSON object of the response result
    """
    if not data:
        return Response("Bad Request", "Request body cannot be empty and challenge body is required")

    challenge_data = Challenge(**data)
    is_valid, err = challenge_data.validate()

    if not is_valid:
        return Response("Bad request", err)
    else:
        challenge = challenge_data.to_dict()
        try:
            challenge_collection = db_connection.get_db_collection()

            res = challenge_collection.insert_one(challenge)
            if res.inserted_id:
                return Response("Successfully created", challenge).to_dict()
            else:
                return Response("Internal Server Error", "Data was not inserted properly into the database")
        except errors.DuplicateKeyError as e:
            return Response("Bad Request", f"Image URL {challenge['image_url']} is duplicated!").to_dict()

if __name__ == '__main__':
    for data in test.create_users():
        print(f'{add_challenge(data)}\n')
    print(get_all_challenges())
    print(get_challenge_by_ids({"_id": [ "6524bec1adb7238a3c812a8b" ]}))