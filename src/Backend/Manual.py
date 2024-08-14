from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import cv2
import sys

app = Flask(__name__)
CORS(app)
IMAGE_DIRECTORY = '../assets/DispImages'
CROPPED_IMAGE_DIRECTORY = '../assets/CroppedImages'
DATA_FILE = '../../Data/details.txt'  # File to store details
global_count = 0

# Ensure directories exist
if not os.path.exists(CROPPED_IMAGE_DIRECTORY):
    os.makedirs(CROPPED_IMAGE_DIRECTORY)


def crop_image(image_path, x, y):
    global global_count
    image = cv2.imread(image_path)

    xco = int(x)
    yco = int(y)

    height, width, _ = image.shape
    crop_size = 100

    x_start = max(xco - crop_size, 0)
    x_end = min(xco + crop_size, width)
    y_start = max(yco - crop_size, 0)
    y_end = min(yco + crop_size, height)

    crop = image[y_start:y_end, x_start:x_end]

    print(f'Received coordinates: x={xco}, y={yco}', file=sys.stderr)

    cropped_image_filename = f'cropped_image_{global_count}.png'
    cropped_image_path = os.path.join(
        CROPPED_IMAGE_DIRECTORY, cropped_image_filename)
    cv2.imwrite(cropped_image_path, crop)

    global_count += 1

    return cropped_image_filename


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

    image_path = os.path.join(IMAGE_DIRECTORY, image_url)
    cropped_image_filename = crop_image(image_path, x, y)
    cropped_image_url = f'http://127.0.0.1:9080/cropped-images/{
        cropped_image_filename}'

    return jsonify({'croppedImageUrl': cropped_image_url})


@app.route('/cropped-images/<filename>', methods=['GET'])
def get_cropped_image(filename):
    return send_from_directory(CROPPED_IMAGE_DIRECTORY, filename)


@app.route('/save-details', methods=['POST'])
@app.route('/save-details', methods=['POST'])
def save_details():
    try:
        data = request.json
        image_name = data.get('croppedImageUrl', '').split('/')[-1]
        shape = data.get('shape', '')
        colour = data.get('colour', '')
        alphanumeric = data.get('alphanumeric', '')
        alphanumeric_colour = data.get('alphanumericColour', '')

        # Print debug information
        print(f"Received data: {image_name}, {shape}, {colour}, {
              alphanumeric}, {alphanumeric_colour}", file=sys.stderr)

        # Write to file
        with open(DATA_FILE, 'a') as f:
            f.write(f'{image_name}: Shape={shape}, Colour={colour}, Alphanumeric={
                    alphanumeric}, Alphanumeric Colour={alphanumeric_colour} \n')
            f.flush()  # Ensure the buffer is flushed

        return jsonify({'message': 'Details saved successfully'}), 200
    except Exception as e:
        # Print error message
        print(f"Error saving details: {str(e)}", file=sys.stderr)
        return jsonify({'message': f'Failed to save details: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(port=9080)
