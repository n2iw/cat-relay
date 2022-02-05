import socket
import sys
import time

from radio_info import get_radio_info
from hamlib import HamLibClient
from dxlab import Commander

UDP_IP = "127.0.0.1"
UDP_PORT = 13063

HAMLIB_IP = '127.0.0.1'
HAMLIB_PORT = 4532

CMDR_IP = '127.0.0.1'
CMDR_PORT = 5555

RETRY_TIME = 10  # seconds
SYNC_INTERVAL = 0.05  # seconds

if __name__ == '__main__':
    # reconnect every RETRY_TIME seconds, until user press Ctrl+C
    while True:
        try:
            with HamLibClient(HAMLIB_IP, HAMLIB_PORT) as hamlib:
                with Commander(CMDR_IP, CMDR_PORT) as cmdr:
                    new_freq = None
                    while True:
                        cmdr_freq = cmdr.get_freq()
                        hl_freq = hamlib.get_freq()
                        if cmdr_freq != new_freq and isinstance(cmdr_freq, int):
                            new_freq = cmdr_freq
                            hamlib.set_freq(new_freq)
                        elif hl_freq != new_freq and isinstance(hl_freq, int):
                            new_freq = hl_freq
                            cmdr.set_freq(new_freq)
                        time.sleep(SYNC_INTERVAL)
        except KeyboardInterrupt as ke:
            print("\nTerminated by user.")
            sys.exit()
        except Exception as e:
            print(e)
            print(f'Retry in {RETRY_TIME} seconds ...')
            print('Press Ctrl+C to exit')
            time.sleep(RETRY_TIME)





