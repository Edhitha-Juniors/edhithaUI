from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import cv2
import sys

app = Flask(__name__)
CORS(app)
IMAGE_DIRECTORY = '../assets/DispImages'
CROPPED_IMAGE_DIRECTORY = '../assets/CroppedImages'
global_count = 0

# Ensure cropped images directory exists
if not os.path.exists(CROPPED_IMAGE_DIRECTORY):
    os.makedirs(CROPPED_IMAGE_DIRECTORY)


def crop_image(image_path, x, y):
    global global_count
    image = cv2.imread(image_path)

    xco = int(x)  # Ensure x is an integer
    yco = int(y)  # Ensure y is an integer

    print(f'Received coordinates: x={xco}, y={yco}', file=sys.stderr)


@app.route('/all-images', methods=['GET'])
def all_images():
    images = os.listdir(IMAGE_DIRECTORY)
    return jsonify({'imageUrls': images})


@app.route('/images/<filename>', methods=['GET'])
def get_image(filename):
    return send_from_directory(IMAGE_DIRECTORY, filename)


@app.route('/crop-image', methods=['POST'])
def crop_image_endpoint():
    data = request.json
    image_url = data['imageUrl']
    x = int(data['x'])  # Ensure x is an integer
    y = int(data['y'])  # Ensure y is an integer

    # Print coordinates to console
    print(f'Received coordinates: x={x}, y={y}', file=sys.stderr)

    image_path = os.path.join(IMAGE_DIRECTORY, image_url)
    cropped_image_filename = crop_image(image_path, x, y)
    cropped_image_url = f'/cropped-images/{cropped_image_filename}'

    return jsonify({'croppedImageUrl': None})


@app.route('/cropped-images/<filename>', methods=['GET'])
def get_cropped_image(filename):
    return send_from_directory(CROPPED_IMAGE_DIRECTORY, filename)


if __name__ == '__main__':
    app.run(port=9080)
