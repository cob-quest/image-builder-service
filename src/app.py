from flask import Flask, request, jsonify
from image_build_util import handle_message

app = Flask(__name__)

@app.route('/')
def health_check():
    return jsonify(
        {
            "message": "Image Builder service is up"
        }
    ), 200

@app.route("/build-image", methods=['POST'])
def build_image():
    if handle_message(request.get_json()):
        return jsonify(
            {
                "message": "Image built!"
            }
        ), 201
        
    else:
        return jsonify(
            {
                "error": "Image build failed!"
            }
        ), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)