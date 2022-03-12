#!/usr/bin/env python3

import os
import sys
import time
import yaml

from hamlib import HamLibClient
from dxlab import Commander
from n1mm import N1MMClient
from flrig import FlrigClient

HAMLIB_IP = 'SDR_IP'
HAMLIB_PORT = 'SDR_PORT'

LOGGER_IP = 'Logger_IP'
LOGGER_PORT = 'Logger_PORT'

RADIO_INFO_PORT = 'RADIO_INFO_PORT'
RADIO_FLRIG_IP = 'RADIO_FLDIGI_IP'
RADIO_FLRIG_PORT = 'RADIO_FLDIGI_PORT'

RETRY_TIME = 'Reconnect_time'  # seconds
SYNC_INTERVAL = 'Sync_time'  # seconds

LOGGER_MODE = 'Logger_Mode'

CONFIG_FILE = 'config.yml'


def get_parameters():
    config = {
        HAMLIB_IP: '127.0.0.1',
        HAMLIB_PORT:  4532,

        LOGGER_IP: '127.0.0.1',
        LOGGER_PORT: 5555,

        RADIO_INFO_PORT: 13063,
        RADIO_FLRIG_IP: '127.0.0.1',
        RADIO_FLRIG_PORT: 12345,

        RETRY_TIME: 10,  # seconds
        SYNC_INTERVAL: 0.05,  # seconds

        LOGGER_MODE: 'dxlab'
    }

    if os.path.isfile(CONFIG_FILE):
        with open(CONFIG_FILE) as c_file:
            file_config = yaml.safe_load(c_file)
            config.update(file_config)
            config[LOGGER_MODE] = config[LOGGER_MODE].lower()
  #         print(config) if you are wondering if everything has been configured correctly.

    return config


def get_logger_client(params):
    mode = params[LOGGER_MODE].lower()
    if mode == 'dxlab':
        print(f'Connecting to Commander at {params[LOGGER_IP]}:{params[LOGGER_PORT]}')
        return Commander(params[LOGGER_IP], params[LOGGER_PORT])
    elif mode == 'wb':
        print(f'Connecting to N1MM at {params[LOGGER_IP]}:{params[LOGGER_PORT]}')
        return N1MMClient(params[RADIO_INFO_PORT], params[LOGGER_IP], params[LOGGER_PORT])
    elif mode == 'flrig':
        print(f'Connecting to FLRig at {params[RADIO_FLRIG_IP]}:{params[RADIO_FLRIG_PORT]}')
        return FlrigClient(params[RADIO_FLRIG_IP], params[RADIO_FLRIG_PORT])

if __name__ == '__main__':
    # reconnect every RETRY_TIME seconds, until user press Ctrl+C
    params = get_parameters()
    while True:
        try:
            print(f'Connecting to SDR at {params[HAMLIB_IP]}:{params[HAMLIB_PORT]}')
            with HamLibClient(params[HAMLIB_IP], params[HAMLIB_PORT]) as sdr:
                print(f'SDR connected.')
                with get_logger_client(params) as radio:
                    print(f'Radio controlling app connected\n')
                    while True:
                        radio_freq = radio.get_freq()
                        radio_mode = radio.get_mode()
                        if (radio_freq and radio_freq != sdr.get_last_freq() and isinstance(radio_freq, int)) or \
                           (radio_mode and radio_mode != sdr.get_last_mode() and isinstance(radio_mode, str)):
                            sdr.set_freq_mode(radio_freq, radio_mode)
                            print(f'Sync from radio to SDR {radio_freq}Hz {radio_mode}')
                        else:
                            sdr_freq = sdr.get_freq()
                            sdr_mode = sdr.get_mode()
                            if (sdr_freq and sdr_freq != radio.get_last_freq() and isinstance(sdr_freq, int)) or \
                                (sdr_mode and sdr_mode != radio.get_last_mode() and isinstance(sdr_mode, str)):
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





