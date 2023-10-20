from bson import ObjectId
from cerberus import Validator

class Image:
    """ 
        Define schema to validate input to prevent invalid formats.
    """
    schema = {
        '_id': {'type': 'string'},
        'email': {'type': 'string', 'required': True},
        'image_name': {'type': 'string', 'required': True},
        'image_ver': {'type': 'string', 'required': True},
    }

    def __init__(self, **kwargs):
        self._id = ObjectId(kwargs.get('_id'))
        self.email = kwargs.get('email')
        self.image_name = kwargs.get('image_name')
        self.image_ver = kwargs.get('image_ver')

    def to_dict(self):
        return {
            "_id": str(self._id),
            "email": self.email,
            "image_name": self.image_name,
            "image_ver": self.image_ver
        }
    
    def validate(self):
        validator = Validator(Image.schema)
        if not validator.validate(self.to_dict()):
            return False, validator.errors
        else:
            return True, []
