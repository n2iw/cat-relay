#!/usr/bin/env python3

import logging
import sys
import time
import asyncio

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
    sync_finished = Signal(dict)
    clients_connected = Signal()
    clients_disconnected = Signal()

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
        self.sync_interval = params.sync_interval
        self._terminate_clients = False

        self.freq_memory: dict[ClientType, int | None] = {
            ClientType.CAT: None,
            ClientType.SDR: None
        }
        self.mode_memory: dict[ClientType, CoreMode | None] = {
            ClientType.CAT: None,
            ClientType.SDR: None
        }

    async def connect_and_run(self):
        try:
            self._terminate_clients = False
            async with self._create_cat_client() as cat_client:
                async with self._create_sdr_client() as sdr_client:
                    if not cat_client or not sdr_client:
                        logger.error('Cat or SDR client not connected')
                        self.clients_disconnected.emit()
                        return
                    else:
                        self.clients_connected.emit()
                    while True:
                        if self._terminate_clients:
                            self.clients_disconnected.emit()
                            return
                        await self.sync(cat_client, sdr_client)
                        await asyncio.sleep(self.sync_interval)
        except Exception as e:
            logger.error(f'Unexpected error during relay operation: {str(e)}')
            self.clients_disconnected.emit()

    def stop(self):
        self._terminate_clients = True

    def _create_sdr_client(self) -> Client:
        ip_address = self.sdr_ip if self.sdr_location == NETWORK else LOCAL_HOST
        logger.info('Connecting to %s at %s:%s', self.sdr_software, ip_address, self.sdr_port)
        if self.sdr_software == SDR_CONNECT:
            return SdrConnectClient(ip_address, self.sdr_port)
        elif self.sdr_software == SDR_PP:
            return SdrPPClient(ip_address, self.sdr_port)
        else:
            message = f'SDR software "{self.sdr_software}" is not supported!'
            logger.error(message)
            raise Exception(message)

    def _create_cat_client(self) -> Client:
        ip_address = self.cat_ip if self.cat_location == NETWORK else LOCAL_HOST
        if self.cat_software in [DXLAB, RUMLOG] :
            logger.info('Connecting to %s at %s:%s', self.cat_software, ip_address, self.cat_port)
            return Commander(ip_address, self.cat_port)
        elif self.cat_software == N1MM:
            logger.info('Connecting to %s at %s:%s', self.cat_software, ip_address, self.cat_port)
            return N1MMClient(self.radio_info_port, ip_address, self.cat_port)
        elif self.cat_software == FLRIG:
            logger.info('Connecting to %s at %s:%s', self.cat_software, ip_address, self.cat_port)
            return FlrigClient(ip_address, self.cat_port)
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

    def update_mode_memory(self, client: ClientType, new_mode: CoreMode | None) -> bool:
        if not new_mode:
            return False
        if new_mode != self.mode_memory[client]:
            self.mode_memory[client] = new_mode
            return True
        else:
            return False

    def map_unsupported_cord_mode(self, mode: CoreMode, client_type: ClientType) -> CoreMode | None:
        if mode == CoreMode.NOT_SUPPORTED:
            previous_mode = self.mode_memory[client_type]
            return previous_mode if previous_mode else None
        else:
            return mode

    async def sync(self, cat_client: Client, sdr_client: Client) -> bool:
        try:
            if not cat_client or not sdr_client:
                logger.error('Cat or SDR client not connected')
                self.clients_disconnected.emit()
                return False
            radio_freq = await cat_client.get_freq()
            radio_mode = self.map_unsupported_cord_mode(await cat_client.get_mode(), ClientType.CAT)
            sdr_freq = await sdr_client.get_freq()
            sdr_mode = self.map_unsupported_cord_mode(await sdr_client.get_mode(), ClientType.SDR)
            radio_freq_changed = self.update_freq_memory(ClientType.CAT, radio_freq)
            radio_mode_changed = self.update_mode_memory(ClientType.CAT, radio_mode)
            sdr_freq_changed = self.update_freq_memory(ClientType.SDR, sdr_freq)
            sdr_mode_changed = self.update_mode_memory(ClientType.SDR, sdr_mode)
            if (radio_freq_changed or radio_mode_changed) and radio_mode:
                if radio_freq != sdr_freq or radio_mode != sdr_mode:
                    await sdr_client.set_freq_mode(radio_freq, radio_mode)
                    self.sync_finished.emit(sync_result(True, 'radio', 'SDR', radio_freq, radio_mode.value))
                    return True
            elif (sdr_freq_changed or sdr_mode_changed) and sdr_mode:
                if sdr_freq != radio_freq or sdr_mode != radio_mode:
                    await cat_client.set_freq_mode(sdr_freq, sdr_mode)
                    self.sync_finished.emit(sync_result(True, 'SDR', 'radio', sdr_freq, sdr_mode.value))
                    return True
            return False
        except Exception as e:
            logger.error(f'Sync failed: {str(e)}')
            return False

async def main():
    setup_logging()
    # reconnect every RETRY_TIME seconds, until user presses Ctrl+C
    params = Config().params
    try:
        cat_relay = CatRelay(params)
        await cat_relay.connect_and_run()

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
    asyncio.run(main())





