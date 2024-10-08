from pymavlink import mavutil
from flask import Flask, jsonify, request, send_from_directory
import threading
import time
from modules.drone_status import drone_state

global is_connected

the_connection = None
is_connected = False


def toggle_connection():
    global the_connection, is_connected
    print("meh")

    # If already connected, close the connection
    if is_connected:
        if the_connection is not None:
            the_connection.close()
            the_connection = None
            is_connected = False
            # Return None for the connection
            print("Disconnected from the drone")

    # Start a new connection to the drone
    try:
        # #the_connection = mavutil.mavlink_connection('tcp:10.42.0.1:5760')
        # the_connection = mavutil.mavlink_connection('udp:10.42.0.55:14555')
        the_connection = mavutil.mavlink_connection('udp:0.0.0.0:14550')
        the_connection.wait_heartbeat()
        print("Heartbeat received from system (system %u component %u)" %
              (the_connection.target_system, the_connection.target_component), flush=True)

        # Set connection status to True only after successful connection
        is_connected = True
        print("Connected successfully!", flush=True)

        threading.Thread(target=monitor_drone_status, daemon=True).start()
        print("Monitoring thread started.", flush=True)

        return the_connection, is_connected

        # return the_connection, is_connected  # Return the connection and its status
    except Exception as e:
        print("failed")
        print(f"Failed to connect to the drone: {
              str(e)}", flush=True)  # Print the error message
        return None, jsonify({'message': f'Failed to connect to the drone: {str(e)}'}), 500


def monitor_drone_status():
    global the_connection, is_connected, drone_state
    while is_connected:
        msg = the_connection.recv_match(
            type=['HEARTBEAT', 'COMMAND_ACK'], blocking=True)

        if msg:
            if msg.get_type() == 'HEARTBEAT':
                drone_state.is_armed = bool(
                    msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED)
                drone_state.current_mode = mavutil.mode_string_v10(msg)
                print(f"Drone Status - Mode: {drone_state.current_mode}, Arm Status: {
                      'Armed' if drone_state.is_armed else 'Disarmed'}", flush=True)

        time.sleep(0.5)
 # Adjust the frequency of status updates as needed


def arm():
    global the_connection
    try:
        the_connection.mav.command_long_send(
            the_connection.target_system, the_connection.target_component, 400, 0, 1, 0, 0, 0, 0, 0, 0)
        msg = the_connection.recv_match(type='COMMAND_ACK', blocking=True)
        global armmsgs
        armmsgs = "armed: " + str(msg)
        return armmsgs
    except Exception as e:
        armmsgs = "Error in arm: " + str(e)
        return armmsgs
        # logging.error("Error in arm: %s", e)


def takeoffcommand():
    global the_connection
    try:
        # Send arm command
        print("Taking off...")

        # Send takeoff command
        the_connection.mav.command_long_send(the_connection.target_system, the_connection.target_component,
                                             mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, 10)

        # Wait for an acknowledgment
        tkfmsg = the_connection.recv_match(type='COMMAND_ACK', blocking=True)
        print(tkfmsg)
        return jsonify({'status': 'success', 'message': str(tkfmsg)}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


def disarm():
    global the_connection
    try:
        the_connection.mav.command_long_send(
            the_connection.target_system, the_connection.target_component, 400, 0, 0, 0, 0, 0, 0, 0, 0)
        msg = the_connection.recv_match(type='COMMAND_ACK', blocking=True)
        global disarmmsgs
        disarmmsgs = "disarmed: " + str(msg)
        return disarmmsgs
    except Exception as e:
        disarmmsgs = "Error in disarm: " + str(e)
        return disarmmsgs
        # logging.error("Error in arm: %s", e)


def auto():
    global the_connection
    try:
        the_connection.mav.command_long_send(
            the_connection.target_system, the_connection.target_component, 176, 0, 1, 3, 0, 0, 0, 0, 0)
        msg = the_connection.recv_match(type='COMMAND_ACK', blocking=True)
        global automsgs
        automsgs = "In auto: " + str(msg)
        return automsgs
    except Exception as e:
        automsgs = "Error in auto: " + str(e)
        return automsgs
        # logging.error("Error in auto: %s", e)


def loiter():
    global the_connection
    try:
        print("Entering Loiter...", flush=True)
        the_connection.mav.command_long_send(
            the_connection.target_system, the_connection.target_component, 176, 0, 1, 5, 0, 0, 0, 0, 0)
        msg = the_connection.recv_match(type='COMMAND_ACK', blocking=True)
        global loitermsgs
        loitermsgs = "In loiter: " + str(msg)
        return loitermsgs
    except Exception as e:
        loitermsgs = "Error in loiter: " + str(e)
        return loitermsgs
        # logging.error("Error in loiter: %s", e)


def guided():
    global the_connection
    try:
        the_connection.mav.command_long_send(
            the_connection.target_system, the_connection.target_component, 176, 0, 1, 4, 0, 0, 0, 0, 0)
        msg = the_connection.recv_match(type='COMMAND_ACK', blocking=True)
        global guidedmsgs
        guidedmsgs = "In loiter: " + str(msg)
        return guidedmsgs
    except Exception as e:
        guidedmsgs = "Error in loiter: " + str(e)
        return guidedmsgs
        # logging.error("Error in loiter: %s", e)


def stabilize():
    global the_connection
    try:
        print("Entering Stabilize...", flush=True)
        the_connection.mav.command_long_send(
            the_connection.target_system, the_connection.target_component, 176, 0, 1, 0, 0, 0, 0, 0, 0)
        msg = the_connection.recv_match(type='COMMAND_ACK', blocking=True)
        global stabilizemsgs
        stabilizemsgs = "In stabalize: " + str(msg)
        return stabilizemsgs
    except Exception as e:
        stabilizemsgs = "Error in stabilize: " + str(e)
        return stabilizemsgs
        # logging.error("Error in loiter: %s", e)


def rtl():
    global the_connection
    try:
        print("Entering RTL...", flush=True)
        the_connection.mav.command_long_send(
            the_connection.target_system, the_connection.target_component, 192, 0, 0, 0, 0, 0, 0, 0, 0)
        msg = the_connection.recv_match(type='COMMAND_ACK', blocking=True)
        global rtlmsgs
        rtlmsgs = "In RTL: " + str(msg)
        return rtlmsgs
    except Exception as e:
        rtlmsgs = "Error in RTL: " + str(e)
        return rtlmsgs
        # logging.error("Error in RTL: %s", e)
