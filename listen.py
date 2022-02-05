import socket
import sys
import time

from radio_info import get_radio_info
from hamlib import HamLibClient

UDP_IP = "127.0.0.1"
UDP_PORT = 13063

HAMLIB_IP = '127.0.0.1'
HAMLIB_PORT = 4532

RETRY_TIME = 10 # seconds

if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    client = None
    while True:
        try:
            with HamLibClient(HAMLIB_IP, HAMLIB_PORT) as client:
                while True:
                    data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
                    print(f'received message from {addr}: {str(data)}')
                    info = get_radio_info(data)
                    if info and info.data:
                        freq = int(info.data['Freq']) * 10
                        print(f'Frequency: {freq}')
                        if client is not None:
                            client.set_freq(freq)
        except KeyboardInterrupt as ke:
            print("\nTerminated by user.")
            sys.exit()
        except Exception as e:
            print(e)
            print(f'Retry in {RETRY_TIME} seconds ...')
            print('Press Ctrl + C to exit')
            time.sleep(RETRY_TIME)





