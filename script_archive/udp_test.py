import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.settimeout(1.0)
message = b'test'
addr = ("127.0.0.1", 10080)

client_socket.sendto(b'test0', addr)
client_socket.sendto(b'test1', addr)
client_socket.sendto(b'test2', addr)