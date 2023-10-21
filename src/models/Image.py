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
        'containerUrl': {'type': 'string', 'required': True},
        's3Path': {'type': 'string', 'required': True}
    }

    def __init__(self, **kwargs):
        self._id = ObjectId(kwargs.get('_id'))
        self.corId = kwargs.get('corId')
        self.creatorName = kwargs.get('creatorName')
        self.imageName = kwargs.get('imageName')
        self.containerUrl = kwargs.get('containerUrl')
        self.s3Path = kwargs.get('s3Path')

    def to_dict(self):
        return {
            "_id": str(self._id),
            "corId": self.corId,
            "creatorName": self.creatorName,
            "imageName": self.imageName,
            "containerUrl": self.containerUrl,
            "s3Path": self.s3Path,
        }
    
    def validate(self):
        validator = Validator(Image.schema)
        if not validator.validate(self.to_dict()):
            return False, validator.errors
        else:
            return True, []
