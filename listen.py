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
                    current_freq = None
                    current_mode = None
                    while True:
                        cmdr_freq = cmdr.get_freq()
                        hl_freq = hamlib.get_freq()
                        hl_mode = hamlib.get_mode()
                        if cmdr_freq != current_freq and isinstance(cmdr_freq, int):
                            current_freq = cmdr_freq
                            hamlib.set_freq(current_freq)
                        elif (hl_freq != current_freq and isinstance(hl_freq, int)) or \
                            (hl_mode != current_mode and isinstance(hl_mode, str)):
                            current_freq = hl_freq
                            current_mode = hl_mode
                            cmdr.set_freq(current_freq, hl_mode)
                        time.sleep(SYNC_INTERVAL)
        except KeyboardInterrupt as ke:
            print("\nTerminated by user.")
            sys.exit()
        except Exception as e:
            print(e)
            print(f'Retry in {RETRY_TIME} seconds ...')
            print('Press Ctrl+C to exit')
            time.sleep(RETRY_TIME)





