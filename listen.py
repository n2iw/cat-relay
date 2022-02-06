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
            with HamLibClient(params[HAMLIB_IP], params[HAMLIB_PORT]) as sdr:
                with Commander(params[CMDR_IP], params[CMDR_PORT]) as radio:
                    while True:
                        radio_freq = radio.get_freq()
                        radio_mode = radio.get_mode()
                        if (radio_freq != sdr.get_last_freq() and isinstance(radio_freq, int)) or \
                           (radio_mode != sdr.get_last_mode() and isinstance(radio_mode, str)):
                            sdr.set_freq_mode(radio_freq, radio_mode)
                            print(f'Sync from radio to SDR {radio_freq}Hz {radio_mode}')
                        else:
                            sdr_freq = sdr.get_freq()
                            sdr_mode = sdr.get_mode()
                            if (sdr_freq != radio.get_last_freq() and isinstance(sdr_freq, int)) or \
                                (sdr_mode != radio.get_last_mode() and isinstance(sdr_mode, str)):
                                radio.set_freq_mode(sdr_freq, sdr_mode)
                                print(f'Sync from SDR to radio {sdr_freq}Hz {sdr_mode}')
                        time.sleep(params[SYNC_INTERVAL])
        except KeyboardInterrupt as ke:
            print("\nTerminated by user.")
            sys.exit()
        except Exception as e:
            print(e)
            print(f'Retry in {params[RETRY_TIME]} seconds ...')
            print('Press Ctrl+C to exit')
            time.sleep(params[RETRY_TIME])





