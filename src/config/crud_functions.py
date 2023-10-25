from src.config.db_connection import get_collection
from pymongo import errors
from src.models.Image import Image
from src.models.Response import Response
from src.logger import logger


class CrudFunctions:

    def __init__(self, client=None):
        self.image_collection = client if client else get_collection()
        

    def get_all_images(self):
        """Get all images

        Returns:
            JSON: JSON objects for all the images that are created
        """

        records = self.image_collection.find()
        
        res = []
        for record in records:
            res.append(record)
            
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
        
        ids = data.get("corId")
        
        if not ids:
            return Response("Bad Request", "A list of images IDs required").to_dict()


        images = self.image_collection.find({"corId": {'$in': ids}})

        res = []
        for image in images:
            res.append(image)
        
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
        
        image = image_data.to_dict()
        try:
            res = self.image_collection.insert_one(image)
            
            logger.info(f"{data['corId']} Written to DB")
            
            if res.inserted_id:
                return Response("Successfully created", image).to_dict()
            else:
                return Response("Internal Server Error", "Data was not inserted properly into the database").to_dict()
            
        except errors.DuplicateKeyError as e:
            logger.error(e)
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
        
        if not data or not data.get('corId'):
            return Response("Bad Request", "Request body and image ID is required").to_dict()

        image_data = Image(**data)
        is_valid, err = image_data.validate()

        if not is_valid:
            return Response("Bad Request", err).to_dict()
        else:
            image = image_data.to_dict()
            id = image.get("corId")
            try:
                res = self.image_collection.find_one_and_update({"corId": id}, {'$set': image})
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
            return Response("Bad Request", "Request body cannot be empty and image corId is required").to_dict()
        
        corIds = data.get("corId")

        # Fetch the documents that match the given corId list before deletion
        cursor = self.image_collection.find({"corId": {"$in": corIds}})
        existing_images = list(cursor)
        existing_corIds = [img["corId"] for img in existing_images]

        # Delete the documents
        res = self.image_collection.delete_many({"corId": {"$in": corIds}})

        # Determine which corIds have been deleted
        deleted_corIds = list(set(corIds) & set(existing_corIds))
        not_deleted_corIds = list(set(corIds) - set(deleted_corIds))

        if res.deleted_count > 0:
            logger.info(f"Deleted images with corIds: {deleted_corIds}")
            if not_deleted_corIds:
                logger.warning(f"Failed to delete images with corIds: {not_deleted_corIds}")
            return Response("Success", deleted_corIds).to_dict()
        else:
            return Response("Internal Server Error", "Unable to delete records").to_dict()

    def delete_all_images(self):
        cursor = self.image_collection.find()
        images = list(cursor)

        deleted = self.image_collection.delete_many({})

        if deleted.acknowledged:
            return Response("Success", images).to_dict()
        else:
            return Response("Internal Server Error", "Unable to delete all records").to_dict()