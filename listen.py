#!/usr/bin/env python3

import sys
import time

from hamlib import HamLibClient
from radio_control.dxlab import Commander
from radio_control.n1mm import N1MMClient
from radio_control.flrig import FlrigClient

from config  import Parameters, DXLAB, N1MM, FLRIG


def get_logger_client(params):
    mode = params.get_logger_mode()
    radio_control_ip = params.get_logger_ip()
    radio_control_port = params.get_logger_port()
    if mode == DXLAB:
        print(f'Connecting to Commander at {radio_control_ip}:{radio_control_port}')
        return Commander(radio_control_ip, radio_control_port)
    elif mode == N1MM:
        radio_info_port = params.get_radio_info_port()
        print(f'Connecting to N1MM at {radio_control_ip}:{radio_control_port}')
        return N1MMClient(radio_info_port, radio_control_ip, radio_control_port)
    elif mode == FLRIG:
        print(f'Connecting to FLRig at {radio_control_ip}:{radio_control_port}')
        return FlrigClient(radio_control_ip, radio_control_port)

if __name__ == '__main__':
    # reconnect every RETRY_TIME seconds, until user press Ctrl+C
    params = Parameters()
    while True:
        try:
            sdr_ip = params.get_sdr_ip()
            sdr_port = params.get_sdr_port()
            print(f'Connecting to SDR at {sdr_ip}:{sdr_port}')
            with HamLibClient(sdr_ip, sdr_port) as sdr:
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
                        time.sleep(params.get_sync_interval())
        except KeyboardInterrupt as ke:
            print("\nTerminated by user.")
            sys.exit()
        except Exception as e:
            retry_time = params.get_retry_time()
            print(e)
            print(f'Retry in {retry_time} seconds ...')
            print('Press Ctrl+C to exit')
            time.sleep(retry_time)





