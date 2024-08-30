#!/usr/bin/env python3

import sys
import time

from sdr_control.hamlib import HamLibClient
from radio_control.dxlab import Commander
from radio_control.n1mm import N1MMClient
from radio_control.flrig import FlrigClient

from config  import Config, DXLAB, N1MM, FLRIG, RUMLOG

MODE = "mode"
FREQUENCY = "frequency"
DESTINATION = "destination"
SOURCE = "source"
MESSAGE = 'message'

def sync_result(source, destination, frequency, mode):
    return {
        MESSAGE: f'Sync from {source} to {destination} {frequency}Hz {mode}',
        SOURCE: source,
        DESTINATION: destination,
        FREQUENCY: frequency,
        MODE: mode
    }

class CatRelay:
    def __init__(self, params):
        self.cat_mode = params.cat_software
        self.cat_ip = params.cat_ip
        self.cat_port = params.cat_port
        self.radio_info_port = params.radio_info_port
        self.sdr_ip = params.sdr_ip
        self.sdr_port = params.sdr_port

        self.cat_client = None
        self.sdr_client = None

    def set_params(self, params):
        self.cat_mode = params.cat_software
        self.cat_ip = params.cat_ip
        self.cat_port = params.cat_port
        self.radio_info_port = params.radio_info_port
        self.sdr_ip = params.sdr_ip
        self.sdr_port = params.sdr_port

    def connect(self):
        self.cat_client = self._connect_cat()
        print(f'Cat Software connected\n')

        self.sdr_client = self._connect_sdr()
        print(f'SDR connected.')

    def disconnect(self):
        if self.cat_client:
            self.cat_client.close()
            self.cat_client = None

        if self.sdr_client:
            self.sdr_client.close()
            self.sdr_client = None

    def __del__(self):
        self.disconnect()

    def _connect_sdr(self):
        print(f'Connecting to SDR at {self.sdr_ip}:{self.sdr_port}')
        return HamLibClient(self.sdr_ip, self.sdr_port).__enter__()

    def _connect_cat(self):
        if self.cat_mode in [DXLAB, RUMLOG] :
            print(f'Connecting to Commander at {self.cat_ip}:{self.cat_port}')
            return  Commander(self.cat_ip, self.cat_port).__enter__()
        elif self.cat_mode == N1MM:
            print(f'Connecting to N1MM at {self.cat_ip}:{self.cat_port}')
            return N1MMClient(self.radio_info_port, self.cat_ip, self.cat_port).__enter__()
        elif self.cat_mode == FLRIG:
            print(f'Connecting to FLRig at {self.cat_ip}:{self.cat_port}')
            return FlrigClient(self.cat_ip, self.cat_port).__enter__()
        else:
            message = f'Cat software "{self.cat_mode}" is not supported!'
            print(message)
            raise Exception(message)

    def sync(self):
        radio_freq = self.cat_client.get_freq()
        radio_mode = self.cat_client.get_mode()
        if (radio_freq and radio_freq != self.sdr_client.get_last_freq() and isinstance(radio_freq, int)) or \
                (radio_mode and radio_mode != self.sdr_client.get_last_mode() and isinstance(radio_mode, str)):
            self.sdr_client.set_freq_mode(radio_freq, radio_mode)
            return sync_result('radio', 'SDR', radio_freq, radio_mode)
        else:
            sdr_freq = self.sdr_client.get_freq()
            sdr_mode = self.sdr_client.get_mode()
            if (sdr_freq and sdr_freq != self.cat_client.get_last_freq() and isinstance(sdr_freq, int)) or \
                    (sdr_mode and sdr_mode != self.cat_client.get_last_mode() and isinstance(sdr_mode, str)):
                self.cat_client.set_freq_mode(sdr_freq, sdr_mode)
                return sync_result('SDR', 'radio', sdr_freq, sdr_mode)


if __name__ == '__main__':
    # reconnect every RETRY_TIME seconds, until user press Ctrl+C
    params = Config().params
    while True:
        try:
            cat_relay = CatRelay(params)
            cat_relay.connect()
            while True:
                result = cat_relay.sync()
                if result:
                    print(result[MESSAGE])
                time.sleep(params.sync_interval)

        except KeyboardInterrupt as ke:
            print("\nTerminated by user.")
            cat_relay = None
            sys.exit()
        except Exception as e:
            retry_time = params.reconnect_time
            print(e)
            print(f'Retry in {retry_time} seconds ...')
            print('Press Ctrl+C to exit')
            time.sleep(retry_time)





