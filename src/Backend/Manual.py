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
from modules.drone_status import drone_state

app = Flask(__name__)
CORS(app)

# Directories and File paths
parent_folder = "../../Data/"
IMAGE_DIRECTORY = parent_folder+"/images"
CROPPED_IMAGE_DIRECTORY = parent_folder+"/cropped"
DATA_FILE = '../../Data/details.txt'
csv_path = parent_folder+'/results.csv'
pickle_path = parent_folder+'/cam_wps.pickle'
geo_log_path = parent_folder+"/log/geo_log.txt"
geo_path = "./modules/geotag_on_UI_laptop.py"

# Global variables
global xco, yco, id, lats, longs, connection
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
    print('Cropping Image...', flush=True)
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

        # print(f"Received data: {image_name}, {
        #       shape}, {colour}, {id}, {label}", file=sys.stderr, flush=True)
        print("Saving Details...")
        # print(xco, yco, flush=True)
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
    global connection, is_connected
    connection, is_connected = toggle_connection()  # Capture the connection

    if is_connected:  # Check if connection is valid
        return jsonify({'message': 'Connected to the drone',
                        'system': connection.target_system,
                        'component': connection.target_component}), 200
    else:
        print(f"Failed to connect to the drone",
              flush=True)  # Print the error message
        return jsonify({'message': 'Failed to connect to the drone'}), 500


@app.route('/drone-status', methods=['GET'])
def get_drone_status():
    print("Current Mode: ", drone_state.current_mode, flush=True)
    return jsonify({
        'current_mode': drone_state.current_mode,
        'is_armed': drone_state.is_armed
    }), 200


@app.route('/arm-disarm', methods=['POST'])
def armdisarm():
    data = request.get_json()
    action = data.get('action')  # Get the action ('arm' or 'disarm')

    try:
        if action == 'arm':
            msgs = arm()  # Call the arm function
        elif action == 'disarm':
            msgs = disarm()  # Call the disarm function
        else:
            raise ValueError('Invalid action')

        return jsonify({'status': 'success', 'message': msgs}), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/change-mode', methods=['POST'])
def change_mode():
    try:
        mode = request.json.get('mode')

        if mode == 'auto':
            msgs = auto()  # Call auto mode function
        elif mode == 'guided':
            msgs = guided()  # Call guided mode function
        elif mode == 'loiter':
            msgs = loiter()  # Call loiter mode function
        elif mode == 'stabilize':
            msgs = stabilize()
        else:
            return jsonify({'status': 'error', 'message': 'Invalid mode'}), 400

        return jsonify({'status': 'success', 'message': msgs}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/takeoff', methods=['POST'])
def takeoffdrone():
    response = takeoffcommand()
    return response


@app.route('/rtl', methods=['GET'])
def rtl_command():
    try:
        # Call the rtl function
        result = rtl()
        return jsonify({"status": "success", "message": result}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    

@app.route('/start_geotagg', methods=['POST'])
def start_geotagg():
    print("running geotag", flush=True)
    global process
    print("running geotag", flush=True)
    process = run_python_file(geo_path)
    global msgs
    msgs = "started geotagg"
    # logging.info("started geotagg")
    return "", 204


@app.route('/reposition', methods=['POST'])
def repos():
    global connection
    # logging.info("bottle drop" )
    # logging.info("Target number bottle is dropping on: %s",target_no )
    print("Moving towards target...", flush="True")
    global msg
    target_no = 0
    msg = "Target number bottle is dropping on: %s"+str(target_no)
    print(lats, longs, id, flush=True)
    lati = lats[id-1]
    longi = longs[id-1]
    # drop()
    automation(lati, longi, id, connection)
    return "", 204


if __name__ == '__main__':
    app.run(debug=True, threaded=True, port=9080)
