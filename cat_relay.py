#!/usr/bin/env python3

import logging
import sys
import time

from PySide6.QtCore import QObject, Signal

from utils.log_config import setup_logging

from sdr_control.sdr_connect import SdrConnectClient
from sdr_control.sdr_pp import SdrPPClient
from radio_control.dxlab import Commander
from radio_control.n1mm import N1MMClient
from radio_control.flrig import FlrigClient
from utils.client import Client, CoreMode
from enum import Enum

from config import Config, DXLAB, N1MM, FLRIG, RUMLOG, NETWORK, LOCAL_HOST, SDR_CONNECT, SDR_PP

logger = logging.getLogger(__name__)

MODE = "mode"
FREQUENCY = "frequency"
DESTINATION = "destination"
SOURCE = "source"
MESSAGE = 'message'
CHANGED = 'changed'

def format_frequency(frequency: int | None) -> str:
    if frequency is None:
        return ''
    hertz = int(frequency)
    if hertz >= 1_000_000_000:
        ghz = hertz // 1_000_000_000
        r = hertz % 1_000_000_000
        mhz = r // 1_000_000
        r = r % 1_000_000
        khz = r // 1_000
        hz = r % 1_000
        return f'{ghz}.{mhz:03d}.{khz:03d}.{hz:03d} GHz'
    if hertz >= 1_000_000:
        mhz = hertz // 1_000_000
        r = hertz % 1_000_000
        khz = r // 1_000
        hz = r % 1_000
        return f'{mhz}.{khz:03d}.{hz:03d} MHz'
    if hertz >= 1_000:
        khz = hertz // 1_000
        hz = hertz % 1_000
        return f'{khz}.{hz:03d} kHz'
    return f'{hertz} Hz'

def sync_result(changed, source = None, destination = None, frequency = None, mode = None) -> dict:
    result = {
        CHANGED: changed,
    }
    if changed:
        result.update({
            MESSAGE: f'Sync from {source} to {destination} {format_frequency(frequency)} {mode if mode is not None else ''}',
            SOURCE: source,
            DESTINATION: destination,
            FREQUENCY: frequency,
            MODE: mode
        })
    return result

class ClientType(Enum):
    CAT = 'cat'
    SDR = 'sdr'

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

        self.cat_client: Client|None = None
        self.sdr_client: Client|None = None

        self.freq_memory: dict[ClientType, int | None] = {
            ClientType.CAT: None,
            ClientType.SDR: None
        }
        self.mode_memory: dict[ClientType, CoreMode | None] = {
            ClientType.CAT: None,
            ClientType.SDR: None
        }

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
            self._connect_cat()
            logger.info('Cat Software connected')

            self._connect_sdr()
            logger.info('SDR connected.')

        except Exception as e:
            logger.exception(f'Connection failed: {e}')
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

    def _connect_sdr(self) -> None:
        ip_address = self.sdr_ip if self.sdr_location == NETWORK else LOCAL_HOST
        logger.info('Connecting to %s at %s:%s', self.sdr_software, ip_address, self.sdr_port)
        if self.sdr_software == SDR_CONNECT:
            self.sdr_client = SdrConnectClient(ip_address, self.sdr_port)
            if self.sdr_client:
                self.sdr_client.open()
        elif self.sdr_software == SDR_PP:
            self.sdr_client = SdrPPClient(ip_address, self.sdr_port)
            if self.sdr_client:
                self.sdr_client.open()
        else:
            message = f'SDR software "{self.sdr_software}" is not supported!'
            logger.error(message)
            raise Exception(message)

    def _connect_cat(self) -> None:
        ip_address = self.cat_ip if self.cat_location == NETWORK else LOCAL_HOST
        if self.cat_software in [DXLAB, RUMLOG] :
            logger.info('Connecting to %s at %s:%s', self.cat_software, ip_address, self.cat_port)
            self.cat_client = Commander(ip_address, self.cat_port)
            if self.cat_client:
                self.cat_client.open()
        elif self.cat_software == N1MM:
            logger.info('Connecting to %s at %s:%s', self.cat_software, ip_address, self.cat_port)
            self.cat_client = N1MMClient(self.radio_info_port, ip_address, self.cat_port)
            if self.cat_client:
                self.cat_client.open()
        elif self.cat_software == FLRIG:
            logger.info('Connecting to %s at %s:%s', self.cat_software, ip_address, self.cat_port)
            self.cat_client = FlrigClient(ip_address, self.cat_port)
            if self.cat_client:
                self.cat_client.open()
        else:
            message = f'Cat software "{self.cat_software}" is not supported!'
            logger.error(message)
            raise Exception(message)

    def update_freq_memory(self, client: ClientType, new_freq: int) -> bool:
        if new_freq != self.freq_memory[client]:
            self.freq_memory[client] = new_freq
            return True
        else:
            return False

    def update_mode_memory(self, client: ClientType, new_mode: CoreMode) -> bool:
        if new_mode != self.mode_memory[client]:
            self.mode_memory[client] = new_mode
            return True
        else:
            return False

    async def sync(self):
        try:
            if not self.cat_client or not self.sdr_client:
                logger.error('Cat or SDR client not connected')
                return None
            radio_freq = self.cat_client.get_freq()
            radio_mode = self.cat_client.get_mode()
            sdr_freq = self.sdr_client.get_freq()
            sdr_mode = self.sdr_client.get_mode()
            radio_freq_changed = self.update_freq_memory(ClientType.CAT, radio_freq)
            radio_mode_changed = self.update_mode_memory(ClientType.CAT, radio_mode)
            sdr_freq_changed = self.update_freq_memory(ClientType.SDR, sdr_freq)
            sdr_mode_changed = self.update_mode_memory(ClientType.SDR, sdr_mode)
            if radio_freq_changed or radio_mode_changed:
                if radio_freq != sdr_freq or radio_mode != sdr_mode:
                    self.sdr_client.set_freq_mode(radio_freq, radio_mode)
                    return sync_result(True, 'radio', 'SDR', radio_freq, radio_mode.value)
            elif sdr_freq_changed or sdr_mode_changed:
                if sdr_freq != radio_freq or sdr_mode != radio_mode:
                    self.cat_client.set_freq_mode(sdr_freq, sdr_mode)
                    return sync_result(True, 'SDR', 'radio', sdr_freq, sdr_mode.value)
            return sync_result(False)
        except Exception as e:
            logger.exception(f'Sync failed: {e}')
            self.connection_state_changed.emit(self.is_connected())
            return None

def main():
    setup_logging()
    # reconnect every RETRY_TIME seconds, until user presses Ctrl+C
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

        except KeyboardInterrupt:
            logger.info('Terminated by user.')
            sys.exit()
        except Exception  as e:
            retry_time = params.reconnect_time
            logger.exception(f'Error in main loop {e}')
            logger.info('Retry in %s seconds ...', retry_time)
            logger.info('Press Ctrl+C to exit')
            time.sleep(retry_time)

if __name__ == '__main__':
    main()





