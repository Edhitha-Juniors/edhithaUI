import subprocess
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import cv2
import signal
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pymavlink import mavutil
from modules.mavlink_commands import *
from modules.latlon import *
from modules.automation import *
from modules.drone_status import drone_state
from modules.logger_config import *
import logging
from flask_socketio import SocketIO, emit


app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="http://localhost:5173")

# # Set the SocketIO instance for logging
# set_socketio_instance(socketio)

# Setup logging
setup_logging(socketio) 

@socketio.on('connect')
def handle_connect():
    logging.getLogger().status('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    reason = request.args.get('reason', 'unknown')  # Retrieve the reason for disconnection
    logging.getLogger().status(f'Client disconnected. Reason: {reason}')



CORS(app)


# Directories and File paths
parent_folder = "../../Data/Test"
IMAGE_DIRECTORY = parent_folder+"/images"
CROPPED_IMAGE_DIRECTORY = parent_folder+"/cropped"
DATA_FILE = '../../Data/details.txt'
csv_path = parent_folder+'/results.csv'
pickle_path = parent_folder+'/cam_wps.pickle'
geo_log_path = parent_folder+"/geo_log.txt"
geo_path = "./modules/geotag_on_UI_laptop.py"

# Global variables
global xco, yco, id, lats, longs, connection, process
global_count = 0
connection = None
is_connected = False
the_connection = None
lats = ["null", "null", "null", "null", "null"]
longs = ["null", "null", "null", "null", "null"]

# Ensure directories exist
if not os.path.exists(CROPPED_IMAGE_DIRECTORY):
    os.makedirs(CROPPED_IMAGE_DIRECTORY, exist_ok=True)

if not os.path.exists(IMAGE_DIRECTORY):
    os.makedirs(IMAGE_DIRECTORY, exist_ok=True)

class ImageEventHandler(FileSystemEventHandler):
    """Handles file system events for the image directory."""
    
    def on_created(self, event):
        if event.is_directory:
            return
        self.emit_image_update()

    def on_deleted(self, event):
        if event.is_directory:
            return
        self.emit_image_update()

    def on_modified(self, event):
        if event.is_directory:
            return
        self.emit_image_update()

    def emit_image_update(self):
        """Emit updated image URLs to connected clients."""
        images = os.listdir(IMAGE_DIRECTORY)
        socketio.emit('image_update', {'imageUrls': images})

def start_watching():
    """Start watching the image directory for changes."""
    event_handler = ImageEventHandler()
    observer = Observer()
    observer.schedule(event_handler, IMAGE_DIRECTORY, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)  # Keep the main thread alive
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

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

    
    logging.getLogger().status(f'Received coordinates: x={xco}, y={yco}')
    logging.getLogger().status('Cropping Image...')
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

def stop_python_file():
    global process
    try:
        os.kill(process.pid, signal.SIGTERM)  # Send SIGTERM signal to the process
        logging.info("Python file stopped successfully.")
    except ProcessLookupError:
        logging.info("Process not found. It may have already stopped.")


@app.route('/all-images', methods=['GET'])
def all_images():
    with os.scandir(IMAGE_DIRECTORY) as entries:
        # Filter to include only files (skip directories) and sort by name if desired
        images = [entry.name for entry in entries if entry.is_file()]
        images.sort()
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
    cropped_image_url = f'http://127.0.0.1:9080/cropped-images/{cropped_image_filename}'

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

        logging.getLogger().status(f"Received data: {image_name}, {shape}, {colour}, {id}, {label}")
        logging.getLogger().status("Saving Details...")
        # print(xco, yco, flush=True)
        lats, longs = lat_long_calculation(csv_path, image_url, image_name, xco, yco, id)
        latz, longz = lats[id-1], longs[id-1]
        # Write to file
        with open(DATA_FILE, 'a') as f:
            f.write(f'{image_name}: Lat={latz}, Long={longz}, id={id}, Label={label}\n')
            f.flush()
        logging.getLogger().status("Saved Succesfully.")
        return jsonify({'message': 'Details saved successfully', 'latitude': latz, 'longitude': longz}), 200
    except Exception as e:
        # print(f"Error saving details: {str(e)}", file=sys.stderr)
        logging.getLogger().status(f"Error saving details: {str(e)}")
        return jsonify({'message': f'Failed to save details: {str(e)}'}), 500


# Endpoint for connecting to the drone
@app.route('/toggle-connection', methods=['POST'])
def connectDrone():
    global connection, is_connected
    connection, is_connected = toggle_connection()  # Capture the connection

    if is_connected: 
        logging.getLogger().status("Connection Successfull...") # Check if connection is valid
        return jsonify({'message': 'Connected to the drone',
                        'system': connection.target_system,
                        'component': connection.target_component}), 200
    else:
        logging.getLogger().status(f"Failed to connect to the drone")  # Print the error message
        return jsonify({'message': 'Failed to connect to the drone'}), 500


@app.route('/drone-status', methods=['GET'])
def get_drone_status():
    # print("Current Mode: ", drone_state.current_mode, flush=True)
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

@app.route('/RTL', methods=['POST'])
def rtl():
    response = rtlcommand()
    return response

@app.route('/drop', methods=['POST'])
def dropPkg():
    # Call the drop function
    drop()
    return "Drop command executed", 200  # Respond with a success message

@app.route('/lock-servo', methods=['POST'])
def lockservo():
    # Call the drop function
    lock()
    return "Drop command executed", 200  # Respond with a success message


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
    global process
    process = run_python_file(geo_path)
    global msgs
    msgs = "started geotagg"
    logging.getLogger().status("Started geotagg")
    return "", 204

@app.route('/stop_geotagg', methods=['POST'])
def stop_geotagg():
    stop_python_file()
    global msgs
    msgs="stopped geotagg"
    logging.info("stopped geotagg")
    return "", 204


@app.route('/reposition', methods=['POST'])
def repos():
    print("LALA",flush=True)
    global connection
    # logging.info("bottle drop" )
    # logging.info("Target number bottle is dropping on: %s",target_no )
    # print("Moving towards target...", flush="True")
    global msg
    target_no = 0
    msg = "Target number bottle is dropping on: %s"+str(target_no)
    # print(lats, longs, id, flush=True)
    lati = lats[id-1]
    longi = longs[id-1]
    # drop()
    logging.getLogger().status(lati)
    automation(lati, longi, id, connection)
    return "", 204


if __name__ == '__main__':
    socketio.start_background_task(target=start_watching)
    socketio.run(app, debug=False, port=9080, allow_unsafe_werkzeug=True)
