from src.db import db_connection
from pymongo import errors
from src.models.Challenge import Challenge
from src.models.Response import Response


class CrudFunctions:
    def __init__(self, client=None):
        self.challenge_collection = client if client else db_connection.get_collection()
        

    def get_all_challenges(self):
        """Get all challenges

        Returns:
            JSON: JSON objects for all the challenges that are created
        """

        records = self.challenge_collection.find()
        
        res = {}
        for record in records:
            id = record.pop('_id')
            res[id] = record
            
        if records:
            return Response("Success", res).to_dict()
        else:
            return Response("Internal Server Error", "Unable to read data").to_dict()


    def get_challenge_by_ids(self, data={}):
        """Get challenges by the IDs provided;
            `_id` must be provided with a List value.

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


        challenges = self.challenge_collection.find({"_id": {'$in': ids}})

        res = {}
        for challenge in challenges:
            challenge_id = challenge.pop("_id")
            res[challenge_id] = challenge
        
        if len(res) == len(ids):
            return Response("Success", res).to_dict()
        else:
            not_found = [id for id in ids if id not in res]
            return Response("Not Found", { "Found": res, "Not Found": not_found }).to_dict()


    def add_challenge(self, data={}):
        """ Add a challenge into the database;
            Only 1 request body is required.

        Returns:
            JSON: JSON object of the response result
        """
        if not data:
            return Response("Bad Request", "Request body cannot be empty and challenge body is required").to_dict()

        challenge_data = Challenge(**data)
        is_valid, err = challenge_data.validate()

        if not is_valid:
            return Response("Bad request", err).to_dict()
        else:
            challenge = challenge_data.to_dict()
            try:
                res = self.challenge_collection.insert_one(challenge)
                if res.inserted_id:
                    return Response("Successfully created", challenge).to_dict()
                else:
                    return Response("Internal Server Error", "Data was not inserted properly into the database").to_dict()
                
            except errors.DuplicateKeyError as e:
                print(e)
                return Response("Bad Request", f"Image name and version is duplicated!").to_dict()


    def update_challenge_by_id(self, data={}):
        """Update a challenge by ID;
            Only 1 request body is required.

        Args:
            id (string): A string that represents the ObjectID of the challenge. Defaults to empty string "".

        Returns:
            JSON: JSON object of the response result
        """
        if not data:
            return Response("Bad Request", "Request body cannot be empty and a challenge ID is required").to_dict()
        
        if not data or not data.get('_id'):
            return Response("Bad Request", "Request body and challenge ID is required").to_dict()

        challenge_data = Challenge(**data)
        is_valid, err = challenge_data.validate()

        if not is_valid:
            return Response("Bad Request", err).to_dict()
        else:
            challenge = challenge_data.to_dict()
            id = challenge.pop("_id")
            try:
                res = self.challenge_collection.find_one_and_update({"_id": id}, {'$set': challenge})
                if res:
                    return Response("Success", challenge).to_dict()
                else:
                    return Response("Not Found", "Challenge not found").to_dict()
            except errors.DuplicateKeyError as e:
                return Response("Bad Request", f"Image name and version is duplicated!").to_dict()


    def delete_challenges_by_ids(self, data={}):
        """Delete all the challenges by ID; 
            `_id` must be provided with a List value.

        Args:
            data (dict, optional): A dict object that consists of a key of '_id' and a list of IDs. Defaults to {}.

        Returns:
            JSON: JSON object of the deleted records result
        """
        if not data:
            return Response("Bad Request", "Request body cannot be empty and challenge ID is required").to_dict()
        
        ids = data.get("_id")

        if not ids:
            return Response("Bad Request", "A list of challenge IDs required").to_dict()
        
        challenges = self.challenge_collection.find()
        challenge_records = {}

        for challenge in challenges:
            id = challenge.pop("_id")
            challenge_records[id] = challenge

        # for challenge IDs not found in the DB
        not_found = [id for id in ids if id not in challenge_records]
        # for challenge IDs that is found in DB, get the data that is deleted
        found = {id: challenge_records[id] for id in ids if id in challenge_records}
        
        res = self.challenge_collection.delete_many({"_id": {"$in": ids}})
        if res.acknowledged:
            if res.deleted_count == len(ids):
                return Response("Success", found).to_dict()
            else:
                return Response("Not Found", {"Found": found, "Not Found": not_found}).to_dict()
                
        else:
            return Response("Internal Server Error", "Unable to delete all records").to_dict()

    def delete_all_challenges(self):
        challenges = self.challenge_collection.find()
        res = {}

        for challenge in challenges:
            id = challenge.pop("_id")
            res[id] = challenge

        deleted = self.challenge_collection.delete_many({})

        if deleted.acknowledged:
            return Response("Success", res).to_dict()
        else:
            return Response("Internal Server Error", "Unable to delete all records").to_dict()
