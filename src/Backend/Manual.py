from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import cv2
import sys
from pymavlink import mavutil

app = Flask(__name__)
CORS(app)

# Directories and File paths
IMAGE_DIRECTORY = '../assets/DispImages/'
CROPPED_IMAGE_DIRECTORY = '../assets/CroppedImages/'
DATA_FILE = '../../Data/details.txt'  # File to store details

# Global variables
global_count = 0
the_connection = None  # To hold the MAVLink connection
is_connected = False   # Connection status

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
    x = int(data['x'])
    y = int(data['y'])

    image_path = os.path.join(IMAGE_DIRECTORY, image_url)
    cropped_image_filename = crop_image(image_path, x, y)
    cropped_image_url = f'http://127.0.0.1:9080/cropped-images/{
        cropped_image_filename}'

    return jsonify({'croppedImageUrl': cropped_image_url})


@app.route('/cropped-images/<filename>', methods=['GET'])
def get_cropped_image(filename):
    return send_from_directory(CROPPED_IMAGE_DIRECTORY, filename)


@app.route('/save-details', methods=['POST'])
def save_details():
    try:
        data = request.json
        image_name = data.get('croppedImageUrl', '').split('/')[-1]
        shape = data.get('shape', '')
        colour = data.get('colour', '')
        alphanumeric = data.get('alphanumeric', '')
        alphanumeric_colour = data.get('alphanumericColour', '')

        print(f"Received data: {image_name}, {shape}, {colour}, {
              alphanumeric}, {alphanumeric_colour}", file=sys.stderr)

        # Write to file
        with open(DATA_FILE, 'a') as f:
            f.write(f'{image_name}: Shape={shape}, Colour={colour}, Alphanumeric={
                    alphanumeric}, Alphanumeric Colour={alphanumeric_colour}\n')
            f.flush()

        return jsonify({'message': 'Details saved successfully'}), 200
    except Exception as e:
        print(f"Error saving details: {str(e)}", file=sys.stderr)
        return jsonify({'message': f'Failed to save details: {str(e)}'}), 500


# Endpoint for connecting to the drone
@app.route('/toggle-connection', methods=['POST'])
def toggle_connection():
    global the_connection, is_connected

    # If already connected, close the connection
    print("meh")
    if is_connected:
        if the_connection is not None:
            the_connection.close()
            the_connection = None
            is_connected = False
            print("Disconnected from the drone")
        return jsonify({'message': 'Disconnected from the drone'}), 200

    # Start a new connection to the drone
    try:
        the_connection = mavutil.mavlink_connection('udp:0.0.0.0:14553')

        # Wait for the first heartbeat
        print("Attempting to connect to the drone...")
        the_connection.wait_heartbeat()
        print("Heartbeat received from system (system %u component %u)" %
              (the_connection.target_system, the_connection.target_component))

        # Set connection status to True only after successful connection
        is_connected = True

        print("Connected successfully!")
        return jsonify({'message': 'Connected to the drone',
                        'system': the_connection.target_system,
                        'component': the_connection.target_component}), 200
    except Exception as e:
        print(f"Failed to connect to the drone: {
              str(e)}")  # Print the error message
        return jsonify({'message': f'Failed to connect to the drone: {str(e)}'}), 500


@app.route('/takeoff', methods=['POST'])
def takeoff_drone():
    try:
        # Send arm command
        print("triggered")
        the_connection.mav.command_long_send(the_connection.target_system, the_connection.target_component,
                                             mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 1, 0, 0, 0, 0, 0, 0)

        # Wait for an acknowledgment
        msg = the_connection.recv_match(type='COMMAND_ACK', blocking=True)
        print(msg)

        # Send takeoff command
        the_connection.mav.command_long_send(the_connection.target_system, the_connection.target_component,
                                             mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, 10)

        # Wait for an acknowledgment
        msg2 = the_connection.recv_match(type='COMMAND_ACK', blocking=True)
        print(msg2)
        return jsonify({'status': 'success', 'message': str(msg)}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


if __name__ == '__main__':
    app.run(port=9080)
