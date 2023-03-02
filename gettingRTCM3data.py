import socket
import ssl
import base64

# Connection information
#hostname = 'ntrip.data.gnss.ga.gov.au'
hostname = 'rtk2go.com'
#port = 443 # Secure TLS
port = 2101 # No Secure TLS
mountpoint = 'JARS_HIPERV' # Replace with the desired mountpoint

# Set up the socket and connect to the server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#sock = ssl.wrap_socket(sock, ssl_version=ssl.PROTOCOL_TLS)
sock.connect((hostname, port))

# Send the NTRIP request
username = 'yourname@gmail.com' # Replace with your username if required
password = 'none' # Replace with your password if required
request = 'GET /{} HTTP/1.1\r\n'.format(mountpoint) # Replace with the desired mountpoint
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
    print("data receiving")
    if not chunk:
        break
    data += chunk
    #print(data)
print(data)
