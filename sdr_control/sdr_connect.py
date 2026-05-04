# This module is a client for the SDR Connect software provided by SDRPlay

import logging
from utils.cat_client import CATClient
from websockets.sync.client import connect, ClientConnection
import json
import threading
from utils.client import CoreMode

logger = logging.getLogger(__name__)

FREQUENCY_PROPERTY = 'device_vfo_frequency'
MODE_PROPERTY = 'demodulator'

def SdrConnectMessage(event_type: str, property: str, value: str | None = None) -> str:
    message = {
        'event_type': event_type,
        'property': property
    }
    if value is not None:
        message['value'] = value

    return json.dumps(message)

def get_frequency_message() -> str:
    return SdrConnectMessage('get_property', FREQUENCY_PROPERTY)

def set_frequency_message(freq: int) -> str:
    return SdrConnectMessage('set_property', FREQUENCY_PROPERTY, str(freq))

def get_mode_message() -> str:
    return SdrConnectMessage('get_property', MODE_PROPERTY)

def set_mode_message(mode: str) -> str:
    return SdrConnectMessage('set_property', MODE_PROPERTY, mode)

class SdrConnectClient(CATClient):

    NATIVE_TO_CORE_MODES = {
        'WFM': CoreMode.FM,  # WFM mode from SDR Connect will be converted to WFM mode
        'NFM': CoreMode.FM,  # FM mode from SDR Connect will be converted to FM mode
        'SAM': CoreMode.AM  # SAM mode from SDR Connect will be converted to AM mode
    }

    CORE_TO_NATIVE_MODES = {
        CoreMode.FM: 'NFM'
    }

    def get_native_to_core_mode_mapping(self) -> dict[str, CoreMode]:
        return self.NATIVE_TO_CORE_MODES
    
    def get_core_to_native_mode_mapping(self) -> dict[CoreMode, str]:
        return self.CORE_TO_NATIVE_MODES

    def __init__(self, ip, port):
        self._last_mode: str | None = None
        self._last_freq: int | None = None
        self._ip = ip
        self._port = port
        self._ws: ClientConnection | None = None
        self._terminated = False

    def open(self) -> None:
        try:
            self._terminated = False
            self._ws = connect(f'ws://{self._ip}:{self._port}')
            self._query_device_frequency()
            self._query_device_mode()
            self.thread = threading.Thread(target=self.listen)
            self.thread.start()
            super().open()
        except Exception as e:
            logger.error(f'Failed to connect to SdrConnect at {self._ip}:{self._port}: {e}')
            raise e

    # This function will be running in a separate thread and updates self._last_mode and self._last_freq
    def listen(self):
        if not self._ws:
            logger.error('SDR Connect is not connected')
            return
        logger.info('listening SdrConnect in a new thread')
        for message in self._ws:
            response = json.loads(message)
            if response['event_type'] == 'property_changed':
                if response['property'] == FREQUENCY_PROPERTY:
                    self._last_freq = int(response['value'])
                elif response['property'] == MODE_PROPERTY:
                    native_mode = response['value']
                    self._last_mode = native_mode
            if self._terminated:
                logger.info('Terminated flag detected, terminate the thread')
                return


    def close(self) -> None:
        self._terminated = True
        if self._ws:
            self._ws.close()
            self._ws = None
            self._last_mode = None
            self._last_freq = None
    
    def set_freq_mode(self, freq: int | None, mode: CoreMode | None = None) -> None:
        if not self._ws:
            logger.error('SDR Connect is not connected')
            return

        if freq is not None:
            command = set_frequency_message(freq)
            self._ws.send(command)
            self._last_freq = freq
            self.set_last_freq(freq)

        if mode is not None:
            if self._last_mode != mode:
                native_mode = self.core_to_native_mode(mode)
                command = set_mode_message(native_mode)
                self._ws.send(command)
                self._last_mode = native_mode
                self.set_last_mode(mode)


    def get_freq(self) -> int | None:
        return self._last_freq

    def get_mode(self) -> str | None:
        return self._last_mode

    def _query_device_frequency(self) -> int | None:
        new_freq = self.query_device_property(FREQUENCY_PROPERTY)
        if new_freq is not None:
            self._last_freq = int(new_freq)
        return self._last_freq

    def _query_device_mode(self) -> str | None:
        new_mode = self.query_device_property(MODE_PROPERTY)
        if new_mode is not None:
            self._last_mode = new_mode
        return self._last_mode

    def query_device_property(self, property: str) -> str | None:
        logger.info(f'querying device property: {property}')
        if not self._ws:
            logger.error('SDR Connect is not connected')
            return None
        if property == FREQUENCY_PROPERTY:
            command = get_frequency_message()
        elif property == MODE_PROPERTY:
            command = get_mode_message()
        else:
            logger.error(f'Invalid property: {property}')
            return None
        self._ws.send(command)
        while True:
            response = json.loads(self._ws.recv())
            if response['event_type'] == 'get_property_response' and response['property'] == property:
                new_value = response['value']
                return new_value
            else:
                logger.info(f'ignored event: event_type: {response["event_type"]}, property: {response["property"]}')
        return None
