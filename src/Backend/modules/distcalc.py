import math

def haversine(lat1, long1, lat2, long2):
    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    long1_rad = math.radians(long1)
    lat2_rad = math.radians(lat2)
    long2_rad = math.radians(long2)
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlong = long2_rad - long1_rad
    
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlong / 2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of Earth in kilometers
    radius = 6371.0
    distance = radius * c
    
    print(f"Distance between the points: {distance:.2f} kilometers")