from bson import ObjectId
from cerberus import Validator

class Image:
    """ 
        Define schema to validate input to prevent invalid formats.
    """
    schema = {
        '_id': {'type': 'string'},
        'corId': {'type': 'string', 'required': True},
        'creatorName': {'type': 'string', 'required': True},
        'imageName': {'type': 'string', 'required': True},
        'imageTag': {'type': 'string', 'required': True},
        'imageRegistryLink': {'type': 'string', 'required': True}
    }

    def __init__(self, **kwargs):
        self._id = ObjectId(kwargs.get('_id'))
        self.corId = kwargs.get('corId')
        self.creatorName = kwargs.get('creatorName')
        self.imageName = kwargs.get('imageName')
        self.imageTag = kwargs.get('imageTag')
        self.imageRegistryLink = kwargs.get('imageRegistryLink')

    def to_dict(self):
        return {
            "_id": str(self._id),
            "corId": self.corId,
            "creatorName": self.creatorName,
            "imageName": self.imageName,
            "imageTag": self.imageTag,
            "imageRegistryLink": self.imageRegistryLink
        }
    
    def validate(self):
        validator = Validator(Image.schema)
        if not validator.validate(self.to_dict()):
            return False, validator.errors
        else:
            return True, []
