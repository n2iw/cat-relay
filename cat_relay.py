#!/usr/bin/env python3

import logging
import sys
import time

from PySide6.QtCore import QObject, Signal

from utils.log_config import setup_logging

from sdr_control.hamlib import HamLibClient
from radio_control.dxlab import Commander
from radio_control.n1mm import N1MMClient
from radio_control.flrig import FlrigClient

from config import Config, DXLAB, N1MM, FLRIG, RUMLOG, NETWORK, LOCAL_HOST

logger = logging.getLogger(__name__)

MODE = "mode"
FREQUENCY = "frequency"
DESTINATION = "destination"
SOURCE = "source"
MESSAGE = 'message'
CHANGED = 'changed'

def sync_result(changed, source = None, destination = None, frequency = None, mode = None):
    result = {
        CHANGED: changed,
    }
    if changed:
        result.update({
            MESSAGE: f'Sync from {source} to {destination} {frequency}Hz {mode}',
            SOURCE: source,
            DESTINATION: destination,
            FREQUENCY: frequency,
            MODE: mode
        })
    return result


class CatRelay(QObject):
    # Signals
    connection_state_changed = Signal(bool)

    def __init__(self, params):
        super().__init__()
        self.cat_location = params.cat_location
        self.cat_software = params.cat_software
        self.cat_ip = params.cat_ip
        self.cat_port = params.cat_port
        self.radio_info_port = params.radio_info_port
        self.sdr_software = params.sdr_software
        self.sdr_location = params.sdr_location
        self.sdr_ip = params.sdr_ip
        self.sdr_port = params.sdr_port

        self.cat_client = None
        self.sdr_client = None

    def set_params(self, params):
        self.cat_location = params.cat_location
        self.cat_software = params.cat_software
        self.cat_ip = params.cat_ip
        self.cat_port = params.cat_port
        self.radio_info_port = params.radio_info_port
        self.sdr_software = params.sdr_software
        self.sdr_location = params.sdr_location
        self.sdr_ip = params.sdr_ip
        self.sdr_port = params.sdr_port

    def is_connected(self):
        return self.cat_client is not None and self.sdr_client is not None

    def connect_clients(self):
        try:
            self.cat_client = self._connect_cat()
            logger.info('Cat Software connected')

            self.sdr_client = self._connect_sdr()
            logger.info('SDR connected.')

        except Exception:
            logger.exception('Connection failed')
            self.disconnect_clients()

        finally:
            self.connection_state_changed.emit(self.is_connected())
            return self.is_connected()


    def disconnect_clients(self):
        # save current state
        old_state = self.is_connected()

        if self.cat_client:
            self.cat_client.close()
            self.cat_client = None
            logger.info('Cat Software disconnected')

        if self.sdr_client:
            self.sdr_client.close()
            self.sdr_client = None
            logger.info('SDR disconnected.')

        new_state = self.is_connected()
        if old_state != new_state:
            self.connection_state_changed.emit(self.is_connected())

    def __del__(self):
        self.disconnect_clients()

    def _connect_sdr(self):
        ip_address = self.sdr_ip if self.sdr_location == NETWORK else LOCAL_HOST
        logger.info('Connecting to %s at %s:%s', self.sdr_software, ip_address, self.sdr_port)
        return HamLibClient(ip_address, self.sdr_port).__enter__()

    def _connect_cat(self):
        ip_address = self.cat_ip if self.cat_location == NETWORK else LOCAL_HOST
        if self.cat_software in [DXLAB, RUMLOG] :
            logger.info('Connecting to %s at %s:%s', self.cat_software, ip_address, self.cat_port)
            return  Commander(ip_address, self.cat_port).__enter__()
        elif self.cat_software == N1MM:
            logger.info('Connecting to %s at %s:%s', self.cat_software, ip_address, self.cat_port)
            return N1MMClient(self.radio_info_port, ip_address, self.cat_port).__enter__()
        elif self.cat_software == FLRIG:
            logger.info('Connecting to %s at %s:%s', self.cat_software, ip_address, self.cat_port)
            return FlrigClient(ip_address, self.cat_port).__enter__()
        else:
            message = f'Cat software "{self.cat_software}" is not supported!'
            logger.error(message)
            raise Exception(message)

    def sync(self):
        try:
            radio_freq = self.cat_client.get_freq()
            radio_mode = self.cat_client.get_mode()
            if (radio_freq and radio_freq != self.sdr_client.get_last_freq() and isinstance(radio_freq, int)) or \
                    (radio_mode and radio_mode != self.sdr_client.get_last_mode() and isinstance(radio_mode, str)):
                self.sdr_client.set_freq_mode(radio_freq, radio_mode)
                return sync_result(True, 'radio', 'SDR', radio_freq, radio_mode)
            else:
                sdr_freq = self.sdr_client.get_freq()
                sdr_mode = self.sdr_client.get_mode()
                if (sdr_freq and sdr_freq != self.cat_client.get_last_freq() and isinstance(sdr_freq, int)) or \
                        (sdr_mode and sdr_mode != self.cat_client.get_last_mode() and isinstance(sdr_mode, str)):
                    self.cat_client.set_freq_mode(sdr_freq, sdr_mode)
                    return sync_result(True, 'SDR', 'radio', sdr_freq, sdr_mode)
            return sync_result(False)
        except Exception:
            logger.exception('Sync failed')
            self.connection_state_changed.emit(self.is_connected())
            return None


if __name__ == '__main__':
    setup_logging()
    # reconnect every RETRY_TIME seconds, until user press Ctrl+C
    params = Config().params
    while True:
        try:
            cat_relay = CatRelay(params)
            cat_relay.connect_clients()
            while True:
                result = cat_relay.sync()
                if result:
                    if result[CHANGED]:
                        logger.info(result[MESSAGE])
                else:
                    logger.warning('Sync failed')
                time.sleep(params.sync_interval)

        except KeyboardInterrupt as ke:
            logger.info('Terminated by user.')
            cat_relay = None
            sys.exit()
        except Exception:
            retry_time = params.reconnect_time
            logger.exception('Error in main loop')
            logger.info('Retry in %s seconds ...', retry_time)
            logger.info('Press Ctrl+C to exit')
            time.sleep(retry_time)





