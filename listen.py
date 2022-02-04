import socket

from radio_info import get_radio_info
from hamlib import HamLibClient

UDP_IP = "127.0.0.1"
UDP_PORT = 13063

HAMLIB_IP = '127.0.0.1'
HAMLIB_PORT = 4532


if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    client = None
    try:
        client = HamLibClient(HAMLIB_IP, HAMLIB_PORT)
    except Exception as e:
        print(e)

    while True:
        data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
        print(f'received message from {addr}: {str(data)}')
        info = get_radio_info(data)
        if info and info.data:
            freq = int(info.data['Freq']) * 10
            print(f'Frequency: {freq}')
            if client is not None:
                client.set_freq(freq)



