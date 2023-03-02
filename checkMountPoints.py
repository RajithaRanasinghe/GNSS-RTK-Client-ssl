import socket
import ssl
import base64
import math
from itertools import islice


def parse_mountpoints_info(response, target_lat = -37.914560, target_lon = 145.127381):
    # Split the message into individual mountpoints
    message_str = response.decode('utf-8')
    mountpoints = message_str.split("\r\nSTR;")

    sorted_mp = []
    
    # Loop through the mountpoints and extract the relevant information
    for mountpoint in mountpoints[1:]:
        fields = mountpoint.split(";")
        name = fields[0]
        format = fields[2]
        lat = fields[8]
        lon = fields[9]

    # parse the mountpoint message and extract the mountpoints and their coordinates
        sorted_mp.append({"name": name, "lat": float(lat), "lon": float(lon), "format": format})

    # calculate the distance of each mountpoint from the given latitude and longitude
    for mp in sorted_mp:
        dlat = math.radians(mp["lat"] - target_lat)
        dlon = math.radians(mp["lon"] - target_lon)
        a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(target_lat)) * math.cos(math.radians(mp["lat"])) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        mp["distance"] = 6371 * c


    # sort the mountpoints by their distance from the given latitude and longitude
    sorted_mp = sorted(sorted_mp, key=lambda mp: mp["distance"])
    return sorted_mp

# Connection information
#hostname = 'ntrip.data.gnss.ga.gov.au'
#port = 443 # Secure TLS
hostname = 'rtk2go.com'
port = 2101 # Not secure

# Set up the socket and connect to the server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#sock = ssl.wrap_socket(sock, ssl_version=ssl.PROTOCOL_TLS)  #Uncomment if conneting to a secure conection (port 443)
sock.connect((hostname, port))

# Send the NTRIP request
username = 0 # Replace with your username if required
password = 0 # Replace with your password if required

request = 'GET / HTTP/1.1\r\n'
request += 'Host: {}\r\n'.format(hostname)
request += 'Ntrip-Version: Ntrip/2.0\r\n'
if username:
    auth_string = '{}:{}'.format(username, password).encode('ascii')
    auth_bytes = base64.b64encode(auth_string)
    auth_str = auth_bytes.decode('ascii')
    request += 'Authorization: Basic {}\r\n'.format(auth_str)
request += '\r\n'
sock.sendall(request.encode('ascii'))

# Receive and print the server response
message = b''
while True:
    chunk = sock.recv(4096)
    if not chunk:
        break
    message += chunk


lat = -37.914560
lon = 145.127381
mountpoints = parse_mountpoints_info(message, lat, lon)


print("Closest Mountpoint = {}".format(mountpoints[0]))

# print the sorted mountpoints
for mp in mountpoints[:10]:
    print(f"Name: {mp['name']}, Latitude: {mp['lat']:.4f}, Longitude: {mp['lon']:.4f}, Format: {mp['format']}, Distance: {mp['distance']:.2f} km")


