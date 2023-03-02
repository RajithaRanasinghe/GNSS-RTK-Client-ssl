import socket
import ssl
import base64
import math
import struct


def request_mountpoints(hostname, port, username, password):
    if port == 443:
    # Try connecting with SSL first

        # Set up the socket and connect to the server
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock = ssl.wrap_socket(sock, ssl_version=ssl.PROTOCOL_TLS)
        sock.connect((hostname, port))

        # Send the NTRIP request
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
        sock.settimeout(5)  # timeout after 5 seconds

    elif port == 2101:
        # If connection fails, try connecting without SSL
        
        # Set up the socket and connect to the server
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #sock = ssl.wrap_socket(sock, ssl_version=ssl.PROTOCOL_TLS)
        sock.connect((hostname, port))

        # Send the NTRIP request
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
        sock.settimeout(5)  # timeout after 5 seconds

    else:
        message = "Unsupported port"

    try:
        # Receive and print the server response
        message = b''
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            message += chunk
        
        # close the socket
        sock.close()

    except socket.timeout:
        message = "Socket timed out while waiting for response."


    return message

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

def connect_mountpoint(hostname, port, username, password, mountpoint):
    print("Connecting to {}".format(mountpoint))
    if port == 443:
    # Try connecting with SSL first     
    
        # Set up the socket and connect to the server
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock = ssl.wrap_socket(sock, ssl_version=ssl.PROTOCOL_TLS)
        sock.connect((hostname, port))

    elif port == 2101:
    # If connection fails, try connecting without SSL
        # Set up the socket and connect to the server
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #sock = ssl.wrap_socket(sock, ssl_version=ssl.PROTOCOL_TLS)
        sock.connect((hostname, port))

    else:
        sock = "Error 404"

    return sock

def get_RTCM3_frm_socket(socket, hostname, username, password, mountpoint):

    # Send the NTRIP request
    request = 'GET /{} HTTP/1.1\r\n'.format(mountpoint)
    request += 'Host: {}\r\n'.format(hostname)
    request += 'Ntrip-Version: Ntrip/2.0\r\n'
    if username:
        auth_string = '{}:{}'.format(username, password).encode('ascii')
        auth_bytes = base64.b64encode(auth_string)
        auth_str = auth_bytes.decode('ascii')
        request += 'Authorization: Basic {}\r\n'.format(auth_str)
    request += '\r\n'
    socket.sendall(request.encode('ascii'))

    
    # Receive and print the RTCM3 data
    data = b''
    for i in range (3):
        chunk = socket.recv(4096)
        #print("data receiving")
        if not chunk:
            break
        data += chunk
        #print(data)

    try:
        # extract the HTTP response status code (e.g. "200")
        status_code = data.split(b' ')[1]

        # extract the HTTP response headers
        header_bytes = data.split(b'\r\n\r\n')[0]
        #headers = header_bytes.decode('utf-8')

        # extract the chunk size (e.g. "1da")
        chunk_size_bytes = data.split(b'\r\n')[6]
        #chunk_size = chunk_size_bytes.decode('utf-8')

        #extract the chunk data
        chunk_data_bytes = data.split(b'\r\n')[7]

        chunk_data_with_delimiters = b'\r\n' + chunk_data_bytes + b'\r\n'
    except:
        try:
            #extract the chunk data
            chunk_data_bytes = data.split(b'\r\n')[1]

            chunk_data_with_delimiters = b'\r\n' + chunk_data_bytes + b'\r\n'
        except:
            chunk_data_with_delimiters = data
    

    return chunk_data_with_delimiters

def get_RTCM3_frm_host(hostname, port, username, password, mountpoint):
    try:
        if port == 443:
        # Try connecting with SSL first     
        
            # Set up the socket and connect to the server
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock = ssl.wrap_socket(sock, ssl_version=ssl.PROTOCOL_TLS)
            sock.connect((hostname, port))
            sock.settimeout(3)  # timeout after 3 seconds

        elif port == 2101:
        # If connection fails, try connecting without SSL
            # Set up the socket and connect to the server
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #sock = ssl.wrap_socket(sock, ssl_version=ssl.PROTOCOL_TLS)
            sock.connect((hostname, port))
            sock.settimeout(3)  # timeout after 3 seconds

        request = 'GET /{} HTTP/1.1\r\n'.format(mountpoint) 
        request += 'Host: {}\r\n'.format(hostname)
        request += 'Ntrip-Version: Ntrip/2.0\r\n'
        if username:
            auth_string = '{}:{}'.format(username, password).encode('ascii')
            auth_bytes = base64.b64encode(auth_string)
            auth_str = auth_bytes.decode('ascii')
            request += 'Authorization: Basic {}\r\n'.format(auth_str)
        request += '\r\n'
        sock.sendall(request.encode('ascii'))

        # Receive and print the RTCM3 data
        data = b''
        #while True:
        for i in range (3):
            chunk = sock.recv(4096)
            #print("data receiving")
            if not chunk:
                break
            data += chunk
            #print(data)

        # close the socket
        sock.close()
      
        return parse_rtcm3(data)

    except socket.timeout:
        # close the socket
        sock.close()
        return "\n\nSocket timed out while waiting for response. Mounrpoint could be offline\n"

def parse_rtcm3(data):
    # Parse the data stream using the RTCM3 protocol format
    pos = 0
    while pos < len(data):
        # Check for RTCM3 preamble (0xD3)
        if data[pos] != 0xD3:
            pos += 1
            continue

        # Check for the correct message length
        length = struct.unpack('>H', data[pos+1:pos+3])[0]
        if len(data[pos:]) < length + 3:
            break

        # Extract the RTCM3 message from the data stream
        message = data[pos:pos+length+3]

        # Decode the RTCM3 message using the RTCM3 standard
        # TODO: Implement RTCM3 decoding

        # Extract the relevant information from the decoded message
        # TODO: Extract relevant information

        pos += length + 3

    return message       
   
'''

# Connection information
hostname = 'ntrip.data.gnss.ga.gov.au'
port = 443 # Secure TLS
#port = 2101 # Not secure
username = 'xx' # Replace with your username if required
password = 'xx' # Replace with your password if required
mountpoint = 'CLYT00AUS0' # Replace with the desired mountpoint
lat = -37.914560
lon = 145.127381

message = request_mountpoints(hostname, port, username, password)
mountpoints = parse_mountpoints_info(message, lat, lon)



print("Closest Mountpoint = {}".format(mountpoints[0]['name']))

# print the sorted mountpoints
for mp in mountpoints[:10]:
    print(f"Name: {mp['name']}, Latitude: {mp['lat']:.4f}, Longitude: {mp['lon']:.4f}, Format: {mp['format']}, Distance: {mp['distance']:.2f} km")

sock = connect_mountpoint(hostname, port, username, password, mountpoints[0]['name'])

for i in range(5):
    print(get_RTCM3_frm_socket(sock, username, password, mountpoints[0]['name']))
#print(connect_mountpoint(hostname, port, username, password, mountpoints[0]['name']))

'''



