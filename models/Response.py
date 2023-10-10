class Response:
    def __init__(self, message="success", data={}):
        self.message = message
        self.data = data

    def to_dict(self):
        return {
            "message": self.message,
            "data": self.data
        }
