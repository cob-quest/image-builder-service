from bson import ObjectId
from cerberus import Validator

class Image:
    """ 
        Define schema to validate input to prevent invalid formats.
    """
    schema = {
        '_id': {'type': 'string'},
        'cor_id': {'type': 'string', 'required': True},
        'creator_name': {'type': 'string', 'required': True},
        'image_name': {'type': 'string', 'required': True},
        'image_ver': {'type': 'string', 'required': True},
        'container_url': {'type': 'string', 'required': True},
        's3path': {'type': 'string', 'required': True},
        'timestamp': {'type': 'string', 'required': True},
        'event': {'type': 'string', 'required': True},
        'eventSuccess': {'type': 'boolean', 'required': True},
    }

    def __init__(self, **kwargs):
        self._id = ObjectId(kwargs.get('_id'))
        self.cor_id = kwargs.get('cor_id')
        self.creator_name = kwargs.get('creator_name')
        self.image_name = kwargs.get('image_name')
        self.image_ver = kwargs.get('image_ver')
        self.container_url = kwargs.get('container_url')
        self.s3path = kwargs.get('s3path')

    def to_dict(self):
        return {
            "_id": str(self._id),
            "cor_id": self.cor_id,
            "creator_name": self.creator_name,
            "image_name": self.image_name,
            "image_ver": self.image_ver,
            "container_url": self.container_url,
            "s3path": self.s3path,
        }
    
    def validate(self):
        validator = Validator(Image.schema)
        if not validator.validate(self.to_dict()):
            return False, validator.errors
        else:
            return True, []
