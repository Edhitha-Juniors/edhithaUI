from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)
IMAGE_DIRECTORY = '../assets/DispImages'


@app.route('/all-images', methods=['GET'])
def all_images():
    images = os.listdir(IMAGE_DIRECTORY)
    return jsonify({'imageUrls': images})


@app.route('/images/<filename>', methods=['GET'])
def get_image(filename):
    return send_from_directory(IMAGE_DIRECTORY, filename)


if __name__ == '__main__':
    app.run(port=9080)
