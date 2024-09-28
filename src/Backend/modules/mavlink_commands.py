from pymavlink import mavutil
from flask import Flask, jsonify, request, send_from_directory


def toggle_connection(the_connection, is_connected):
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
        print("Attempting to connect to the drone...", flush=True)
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
        print("failed")
        print(f"Failed to connect to the drone: {
              str(e)}", flush=True)  # Print the error message
        return is_connected, jsonify({'message': f'Failed to connect to the drone: {str(e)}'}), 500
