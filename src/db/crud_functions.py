from db import db_connection
from pymongo import errors
from models.Image import Image
from models.Response import Response


class CrudFunctions:
    def __init__(self, client=None):
        self.image_collection = client if client else db_connection.get_collection()
        

    def get_all_images(self):
        """Get all images

        Returns:
            JSON: JSON objects for all the images that are created
        """

        records = self.image_collection.find()
        
        res = {}
        for record in records:
            id = record.pop('_id')
            res[id] = record
            
        if records:
            return Response("Success", res).to_dict()
        else:
            return Response("Internal Server Error", "Unable to read data").to_dict()


    def get_image_by_ids(self, data={}):
        """Get images by the IDs provided;
            `_id` must be provided with a List value.

        Args:
            data (dict, optional): A dict object that consists of a key of '_id' and a list of IDs. Defaults to {}.

        Returns:
            JSON: JSON objects for all the images that are found.
        """
        if not data:
            return Response("Bad Request", "Request body cannot be empty and images IDs are required").to_dict()
        
        ids = data.get("_id")
        
        if not ids:
            return Response("Bad Request", "A list of images IDs required").to_dict()


        images = self.image_collection.find({"_id": {'$in': ids}})

        res = {}
        for image in images:
            image_id = image.pop("_id")
            res[image_id] = image
        
        if len(res) == len(ids):
            return Response("Success", res).to_dict()
        else:
            not_found = [id for id in ids if id not in res]
            return Response("Not Found", { "Found": res, "Not Found": not_found }).to_dict()


    def add_image(self, data={}):
        """ Add a image into the database;
            Only 1 request body is required.

        Returns:
            JSON: JSON object of the response result
        """
        if not data:
            return Response("Bad Request", "Request body cannot be empty and image body is required").to_dict()

        image_data = Image(**data)
        is_valid, err = image_data.validate()

        if not is_valid:
            return Response("Bad request", err).to_dict()
        else:
            image = image_data.to_dict()
            try:
                res = self.image_collection.insert_one(image)
                if res.inserted_id:
                    return Response("Successfully created", image).to_dict()
                else:
                    return Response("Internal Server Error", "Data was not inserted properly into the database").to_dict()
                
            except errors.DuplicateKeyError as e:
                print(e)
                return Response("Bad Request", f"Image name and version is duplicated!").to_dict()


    def update_image_by_id(self, data={}):
        """Update a image by ID;
            Only 1 request body is required.

        Args:
            id (string): A string that represents the ObjectID of the image. Defaults to empty string "".

        Returns:
            JSON: JSON object of the response result
        """
        if not data:
            return Response("Bad Request", "Request body cannot be empty and a image ID is required").to_dict()
        
        if not data or not data.get('_id'):
            return Response("Bad Request", "Request body and image ID is required").to_dict()

        image_data = Image(**data)
        is_valid, err = image_data.validate()

        if not is_valid:
            return Response("Bad Request", err).to_dict()
        else:
            image = image_data.to_dict()
            id = image.pop("_id")
            try:
                res = self.image_collection.find_one_and_update({"_id": id}, {'$set': image})
                if res:
                    return Response("Success", image).to_dict()
                else:
                    return Response("Not Found", "Image not found").to_dict()
            except errors.DuplicateKeyError as e:
                return Response("Bad Request", f"Image name and version is duplicated!").to_dict()


    def delete_images_by_ids(self, data={}):
        """Delete all the images by ID; 
            `_id` must be provided with a List value.

        Args:
            data (dict, optional): A dict object that consists of a key of '_id' and a list of IDs. Defaults to {}.

        Returns:
            JSON: JSON object of the deleted records result
        """
        if not data:
            return Response("Bad Request", "Request body cannot be empty and image ID is required").to_dict()
        
        ids = data.get("_id")

        if not ids:
            return Response("Bad Request", "A list of image IDs required").to_dict()
        
        images = self.image_collection.find()
        image_records = {}

        for image in images:
            id = image.pop("_id")
            image_records[id] = image

        # for image IDs not found in the DB
        not_found = [id for id in ids if id not in image_records]
        # for image IDs that is found in DB, get the data that is deleted
        found = {id: image_records[id] for id in ids if id in image_records}
        
        res = self.image_collection.delete_many({"_id": {"$in": ids}})
        if res.acknowledged:
            if res.deleted_count == len(ids):
                return Response("Success", found).to_dict()
            else:
                return Response("Not Found", {"Found": found, "Not Found": not_found}).to_dict()
                
        else:
            return Response("Internal Server Error", "Unable to delete all records").to_dict()

    def delete_all_images(self):
        images = self.image_collection.find()
        res = {}

        for image in images:
            id = image.pop("_id")
            res[id] = image

        deleted = self.image_collection.delete_many({})

        if deleted.acknowledged:
            return Response("Success", res).to_dict()
        else:
            return Response("Internal Server Error", "Unable to delete all records").to_dict()
