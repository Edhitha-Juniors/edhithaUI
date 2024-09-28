import subprocess
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import cv2
import sys
from pymavlink import mavutil
from modules.mavlink_commands import *
from modules.latlon import *
from modules.automation import *

app = Flask(__name__)
CORS(app)

# Directories and File paths
parent_folder = "../../Data/"
# IMAGE_DIRECTORY = parent_folder+"/cropped"
IMAGE_DIRECTORY = parent_folder+"/input"
CROPPED_IMAGE_DIRECTORY = parent_folder+"/cropped"
DATA_FILE = '../../Data/details.txt'
csv_path = parent_folder+'/results.csv'
pickle_path = parent_folder+'/cam_wps.pickle'
geo_log_path = parent_folder+"/log/geo_log.txt"
geo_path = "./modules/geotag_on_UI_laptop.py"

# Global variables
global xco, yco, id, lats, longs
global_count = 0
is_connected = False
the_connection = None
lats = ["null", "null", "null", "null", "null"]
longs = ["null", "null", "null", "null", "null"]

# Ensure directories exist
if not os.path.exists(CROPPED_IMAGE_DIRECTORY):
    os.makedirs(CROPPED_IMAGE_DIRECTORY)


def crop_image(image_path, x, y):
    global global_count, xco, yco
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


def run_python_file(file_path):
    # Open the output file in append mode to preserve existing content
    with open(geo_log_path, "a") as f:
        # Start the subprocess with stderr redirected to a pipe
        process = subprocess.Popen(["python", file_path], stdout=f)
    return process


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
    global xco, yco, id, lats, longs
    try:
        data = request.json
        image_url = data.get('selectedImageUrl')
        image_name = data.get('selectedImageUrl', '').split('/')[-1]
        cropped_name = data.get('croppedImageUrl', '').split('/')[-1]
        shape = data.get('shape', '')
        colour = data.get('colour', '')
        id = data.get('id', '')
        label = data.get('label', '')

        print(f"Received data: {image_name}, {
              shape}, {colour}, {id}, {label}", file=sys.stderr, flush=True)
        print(xco, yco, flush=True)
        lats, longs = lat_long_calculation(
            csv_path, image_url, image_name, xco, yco, id)

        # Write to file
        with open(DATA_FILE, 'a') as f:
            f.write(f'{image_name}: Shape={shape}, Colour={
                    colour}, id={id}, Label={label}\n')
            f.flush()

        return jsonify({'message': 'Details saved successfully'}), 200
    except Exception as e:
        print(f"Error saving details: {str(e)}", file=sys.stderr)
        return jsonify({'message': f'Failed to save details: {str(e)}'}), 500


# Endpoint for connecting to the drone
@app.route('/toggle-connection', methods=['POST'])
def connectDrone():
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
        the_connection = mavutil.mavlink_connection('udp:10.42.0.55:14552')

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


@app.route('/start_geotag', methods=['POST'])
def start_geotagg():
    global process
    process = run_python_file(geo_path)
    global msgs
    msgs = "started geotagg"
    # logging.info("started geotagg")
    return "", 204


@app.route('/reposition', methods=['POST'])
def repos():
    # logging.info("bottle drop" )
    # logging.info("Target number bottle is dropping on: %s",target_no )
    print("reposition triggered", flush="True")
    global msg
    target_no = 0
    msg = "Target number bottle is dropping on: %s"+str(target_no)
    lati = lats[id-1]
    longi = longs[id-1]
    print(lati)
    # drop()
    automation(lati, longi, id, the_connection)
    return "", 204


if __name__ == '__main__':
    app.run(debug=True, port=9080)
