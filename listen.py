import os
import sys
import time
import yaml

from hamlib import HamLibClient
from dxlab import Commander

HAMLIB_IP = 'SDR_IP'
HAMLIB_PORT = 'SDR_PORT'

CMDR_IP = 'Logger_IP'
CMDR_PORT = 'Logger_PORT'

RETRY_TIME = 'Reconnect_time'  # seconds
SYNC_INTERVAL = 'Sync_time'  # seconds

CONFIG_FILE = 'config.yml'


def get_parameters():
    config = {
        HAMLIB_IP: '127.0.0.1',
        HAMLIB_PORT:  4532,

        CMDR_IP: '127.0.0.1',
        CMDR_PORT: 5555,

        RETRY_TIME: 10,  # seconds
        SYNC_INTERVAL: 0.05  # seconds
    }

    if os.path.isfile(CONFIG_FILE):
        with open(CONFIG_FILE) as c_file:
            file_config = yaml.safe_load(c_file)
            config.update(file_config)
            print(config)

    return config


if __name__ == '__main__':
    # reconnect every RETRY_TIME seconds, until user press Ctrl+C
    params = get_parameters()
    while True:
        try:
            with HamLibClient(params[HAMLIB_IP], params[HAMLIB_PORT]) as hamlib:
                with Commander(params[CMDR_IP], params[CMDR_PORT]) as cmdr:
                    while True:
                        cmdr_freq = cmdr.get_freq()
                        cmdr_mode = cmdr.get_mode()
                        if (cmdr_freq != hamlib.get_last_freq() and isinstance(cmdr_freq, int)) or \
                           (cmdr_mode != hamlib.get_last_mode() and isinstance(cmdr_mode, str)):
                            hamlib.set_freq_mode(cmdr_freq, cmdr_mode)
                            continue

                        hl_freq = hamlib.get_freq()
                        hl_mode = hamlib.get_mode()
                        if (hl_freq != cmdr.get_last_freq() and isinstance(hl_freq, int)) or \
                            (hl_mode != cmdr.get_last_mode() and isinstance(hl_mode, str)):
                            cmdr.set_freq_mode(hl_freq, hl_mode)
                        time.sleep(params[SYNC_INTERVAL])
        except KeyboardInterrupt as ke:
            print("\nTerminated by user.")
            sys.exit()
        except Exception as e:
            print(e)
            print(f'Retry in {params[RETRY_TIME]} seconds ...')
            print('Press Ctrl+C to exit')
            time.sleep(params[RETRY_TIME])





