# This module is a client for the SDR Connect software provided by SDRPlay

import logging
from utils.client import Client
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
        message['value'] = str(value)

    return json.dumps(message)

def get_frequency_message() -> str:
    return SdrConnectMessage('get_property', FREQUENCY_PROPERTY)

def set_frequency_message(freq: int) -> str:
    return SdrConnectMessage('set_property', FREQUENCY_PROPERTY, freq)

def get_mode_message() -> str:
    return SdrConnectMessage('get_property', MODE_PROPERTY)

def set_mode_message(mode: str) -> str:
    return SdrConnectMessage('set_property', MODE_PROPERTY, mode)

class SdrConnectClient(Client):

    NATIVE_TO_CORE_MODES = {
        'WFM': 'FM',  # WFM mode from SDR Connect will be converted to WFM mode
        'NFM': 'FM',  # FM mode from SDR Connect will be converted to FM mode
        'SAM': 'AM'  # SAM mode from SDR Connect will be converted to AM mode
    }

    CORE_TO_NATIVE_MODES = {
        'FM': 'NFM'
    }

    def __init__(self, ip, port):
        self._last_mode = None
        self._last_freq = None
        self._last_mode_reported = None
        self._last_freq_reported = None
        self._ip = ip
        self._port = port
        self._ws: ClientConnection
        self._terminated = False

    def __enter__(self):
        try:
            self._terminated = False
            self._ws = connect(f'ws://{self._ip}:{self._port}')
            self.query_device_frequency()
            self.query_device_mode()
            self.thread = threading.Thread(target=self.listen)
            self.thread.start()
        except Exception as e:
            logger.error(f'Failed to connect to SdrConnect at {self._ip}:{self._port}: {e}')
            raise e
        return self

    # This function will be running in a separate thread and updates self._last_mode and self._last_freq
    def listen(self):
        logger.info('listening SdrConnect in a new thread')
        for message in self._ws:
            response = json.loads(message)
            if response['event_type'] == 'property_changed':
                if response['property'] == FREQUENCY_PROPERTY:
                    self._last_freq = int(response['value'])
                elif response['property'] == MODE_PROPERTY:
                    native_mode = response['value']
                    self._last_mode = self.NATIVE_TO_CORE_MODES.get(native_mode, native_mode)
            if self._terminated:
                logger.info('Terminated flag detected, terminate the thread')
                return


    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self._terminated = True
        self.close()

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
            self._last_freq_reported = freq

        if mode is not None:
            if self._last_mode != mode:
                native_mode = self.CORE_TO_NATIVE_MODES.get(mode, mode) if mode else None
                command = set_mode_message(native_mode)
                self._ws.send(command)
                self._last_mode = mode
                self._last_mode_reported = mode


    def get_new_freq(self) -> int | None:
        if self._last_freq_reported != self._last_freq:
            self._last_freq_reported = self._last_freq
            return self._last_freq
        else:
            return None

    def get_new_mode(self) -> CoreMode | None:
        if self._last_mode_reported != self._last_mode:
            self._last_mode_reported = self._last_mode
            return self._last_mode
        else:
            return None

    def query_device_frequency(self) -> int | None:
        new_freq = self.query_device_property(FREQUENCY_PROPERTY)
        if new_freq is not None:
            self._last_freq = int(new_freq)
        return self._last_freq

    def query_device_mode(self) -> str | None:
        new_mode = self.query_device_property(MODE_PROPERTY)
        if new_mode is not None:
            self._last_mode = self.NATIVE_TO_CORE_MODES.get(new_mode, new_mode)
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
