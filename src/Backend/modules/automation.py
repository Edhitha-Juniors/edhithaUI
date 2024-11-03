import time
from pymavlink import mavutil
import math
from modules.mavlink_commands import *
from modules.distcalc import *

alti = 21
drop_time = 10

def distance_lat_lon(lat1, lon1, lat2, lon2):
    '''distance between two points'''
    dLat = math.radians(lat2) - math.radians(lat1)
    dLon = math.radians(lon2) - math.radians(lon1)
    a = math.sin(0.5*dLat)**2 + math.sin(0.5*dLon)**2 * \
        math.cos(lat1) * math.cos(lat2)
    c = 2.0 * math.atan2(math.sqrt(abs(a)), math.sqrt(abs(1.0-a)))
    ground_dist = 6371 * 1000 * c
    return ground_dist


# def auto(the_connection):
#     the_connection.mav.command_long_send(
#         the_connection.target_system, the_connection.target_component, 176, 0, 1, 3, 0, 0, 0, 0, 0)
#     msg = the_connection.recv_match(type='COMMAND_ACK', blocking=True)
#     global msgs
#     msgs = "In auto: "+str(msg)
#     # logging.getLogger().status("In auto: %s", msg)``


# def loiter(the_connection):
#     the_connection.mav.command_long_send(
#         the_connection.target_system, the_connection.target_component, 176, 0, 1, 5, 0, 0, 0, 0, 0)
#     msg = the_connection.recv_match(type='COMMAND_ACK', blocking=True)
#     global msgs
#     msgs = "In loiter: "+str(msg)
#     logging.getLogger().status("In loiter: %s", msg, flush=True)


# def guided(the_connection):
#     the_connection.mav.command_long_send(
#         the_connection.target_system, the_connection.target_component, 176, 0, 1, 4, 0, 0, 0, 0, 0)
#     msg = the_connection.recv_match(type='COMMAND_ACK', blocking=True)
#     global msgs
#     msgs = "In guided: "+str(msg)
#     # logging.getLogger().status("In guided: %s", msg)


def inf_drop():
    global the_connection
    logging.getLogger().status("a")
    guided()
    time.sleep(1.5)
    gps = the_connection.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
    # logging.getLogger().status("Current GPS: %s",gps )
    lati = gps.lat
    longi = gps.lon
    logging.getLogger().status("Lat and Long for drop is: ", lati, longi)
    the_connection.mav.send(mavutil.mavlink.MAVLink_set_position_target_global_int_message(
        10, the_connection.target_system, the_connection.target_component, 6, 1024, int(lati), int(longi), alti, 0, 0, 0, 0, 0, 0, 0, 0))
    global msgs
    msgs = "Repositioning for target: "+str(1)


def automation(lati, longi, target_no, the_connection):

    logging.getLogger().status("Automation")
    gps = the_connection.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
    # logging.getLogger().status("GPS during calculation: %s", gps)


    # calculated_distance = distance_lat_lon(lati/1e7, longi/1e7, gps.lat/1e7, gps.lon/1e7)
    # gps = the_connection.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
    # logging.getLogger().status("GPS before shifting to guided: %s", gps)
    kurrentalti = gps.relative_alt/1000
    accuracy = 0.1

    logging.getLogger().status("alti: %s", kurrentalti)
    logging.getLogger().status('Guided')
    guided()
    # drop()
    time.sleep(1.5)
    the_connection.mav.send(mavutil.mavlink.MAVLink_set_position_target_global_int_message(
        10, the_connection.target_system, the_connection.target_component, 6, 1024, int(lati), int(longi), alti, 0, 0, 0, 0, 0, 0, 0, 0))
    """ msg = the_connection.recv_match(type='COMMAND_ACK', blocking=True)
    logging.getLogger().status('Repositioning: ',msg ) """
    global msgs
    msgs = "Repositioning for target: "+str(target_no)

    # logging.getLogger().status("Real_distance between lats and lons: %s",calculated_distance)

    logging.getLogger().status("DESIRED LAT = %s", lati / 1e7)
    logging.getLogger().status("DESIRED LONG = %s", longi / 1e7)

# Wait until the the_connection reaches the target location
    try:
        while True:
            msg = the_connection.recv_match(type=['GLOBAL_POSITION_INT'], blocking=True)
            current_lat = msg.lat / 1e7
            current_lon = msg.lon / 1e7
            distance = distance_lat_lon(current_lat, current_lon, lati/1e7, longi/1e7)
            logging.getLogger().status('distance between the_connection and target: %s', distance)
            global target_dist
            target_dist = "distance = "+str(distance)
            if distance <= accuracy:
                logging.getLogger().status('Started Dropping ...')
                msgs = "starting drop"
                time.sleep(1)
                # drop()

                # the_connection.mav.command_long_send(the_connection.target_system, the_connection.target_component,181, 0, 0, 1, 0, 0, 0, 0, 0)
                time.sleep(drop_time)
                logging.getLogger().status('dropped')
                logging.getLogger().status(
                    'Current drop loc latitude: %s', msg.lat / 1e7)
                logging.getLogger().status(
                    'Current drop loc longtitude: %s', msg.lon / 1e7)

                

                # loiter()
                # the_connection.mav.set_mode_send(the_connection.target_system,mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,17)
                auto()  # Replace with your desired action
                break
    except Exception as e:
        pass