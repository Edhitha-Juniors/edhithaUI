import logging
import datetime
from flask_socketio import SocketIO

# Define the SocketIO instance
socketio = None  # This will be set later

class WebSocketHandler(logging.Handler):
    def emit(self, record):
        msg = self.format(record)
        try:
            if socketio:
                socketio.emit('log_message', {'message': msg})
                print("log emitted", flush=True)
            else:
                print("SocketIO instance not set, cannot emit logs", flush=True)
        except Exception as e:
            print(f"Failed to emit log over WebSocket: {e}")

# Logger configuration
def setup_logging(sio_instance):
    global socketio
    socketio = sio_instance
    # Get the current date and time for the log filename
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = f"../../Data/logs_{current_datetime}.txt"

    # Set up basic logging
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        filename=output_file)

    # Define a StreamHandler to print log messages to the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(message)s')
    console_handler.setFormatter(formatter)

    # Add the WebSocketHandler
    ws_handler = WebSocketHandler()
    ws_handler.setLevel(logging.INFO)
    ws_handler.setFormatter(formatter)

    # Set up the root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(console_handler)
    root_logger.addHandler(ws_handler)  # Add the WebSocket handler

    # Set werkzeug logging level
    # werkzeug_log = logging.getLogger('werkzeug')
    # werkzeug_log.setLevel(logging.WARNING)

# Function to set the SocketIO instance
# def set_socketio_instance(sio_instance):
#     global socketio
#     socketio = sio_instance
