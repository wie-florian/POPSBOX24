#Source: https://www.aranacorp.com/en/setting-up-a-udp-server-on-raspberry-pi/, 07.03.2023
#modified by: Peter Pallnstorfer
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Libraries
import logging
import socket    #https://wiki.python.org/moin/UdpCommunication
#Parameters
localPort=10080
bufferSize=1024
POPS_IP="192.168.7.2"
#Objects
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)  ## Internet,UDP
# function get_ip_address 
def get_ip_address():
    """get host ip address"""
    ip_address = ''
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8",80))
    ip_address = s.getsockname()[0]
    s.close()
    return ip_address
# function init 
def init():
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) #enable broadcasting mode
    sock.bind(('', localPort))
    sock.setblocking(True)         # make the connection nonblocking, returns BlockingIOError when no data in buffer
    logging.info("UDP server : {}:{}".format(get_ip_address(),localPort))
# receive data as string function
def getPOPS():
    latest_pops_data = ""
    try:
        while True:
            logging.debug("reading data from buffer")
            packet  = sock.recvmsg(bufferSize)
            if packet[3][0] == POPS_IP:
                if latest_pops_data != "":
                    logging.warning("There was more than one packet in the buffer")
                    logging.warning(f"discarding data since it is stale: {latest_pops_data}")
                latest_pops_data = packet[0]
                latest_pops_data = str(latest_pops_data.decode().strip())
            else:
                logging.warning(f"received data from unknown ip {packet[3][0]}, discarding")
    except BlockingIOError:
        logging.debug("buffer empty")
        pass
    return latest_pops_data
# function main
def main():
    while True:
        print(getPOPS())

# why do we need this?
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    init()
    main()
