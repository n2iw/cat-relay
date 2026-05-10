# This module is a client for the SDR Connect software provided by SDRPlay
import asyncio
import logging
import json

from websockets.asyncio.client import connect, ClientConnection

from utils.client import CoreMode, Client
from utils.mode_mapper import ModeMapper

logger = logging.getLogger(__name__)

FREQUENCY_PROPERTY = 'device_vfo_frequency'
MODE_PROPERTY = 'demodulator'

def sdr_connect_message(event_type: str, prop: str, value: str | None = None) -> str:
    message = {
        'event_type': event_type,
        'property': prop
    }
    if value is not None:
        message['value'] = value

    return json.dumps(message)

def get_frequency_message() -> str:
    return sdr_connect_message('get_property', FREQUENCY_PROPERTY)

def set_frequency_message(freq: int) -> str:
    return sdr_connect_message('set_property', FREQUENCY_PROPERTY, str(freq))

def get_mode_message() -> str:
    return sdr_connect_message('get_property', MODE_PROPERTY)

def set_mode_message(mode: str) -> str:
    return sdr_connect_message('set_property', MODE_PROPERTY, mode)

class SdrConnectClient(Client):

    NATIVE_TO_CORE_MODES = {
        'WFM': CoreMode.FM,  # WFM mode from SDR Connect will be converted to WFM mode
        'NFM': CoreMode.FM,  # FM mode from SDR Connect will be converted to FM mode
        'SAM': CoreMode.AM  # SAM mode from SDR Connect will be converted to AM mode
    }

    CORE_TO_NATIVE_MODES = {
        CoreMode.FM: 'NFM'
    }

    def __init__(self, ip, port):
        self._last_mode: str | None = None
        self._last_freq: int | None = None
        self._ip = ip
        self._port = port
        self._ws: ClientConnection | None = None
        self._listen_task = None

        self._mapper = ModeMapper(self.CORE_TO_NATIVE_MODES, self.NATIVE_TO_CORE_MODES)

    async def __aenter__(self) -> 'SdrConnectClient':
        self._ws = await connect(f'ws://{self._ip}:{self._port}')
        if not self._ws:
            raise Exception('Fail to connect to SDR Connect')

        await self._query_device_frequency()
        await self._query_device_mode()
        if self._listen_task is None:
            self._listen_task = asyncio.create_task(self.listen())
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        self._listen_task = None
        if self._ws:
            asyncio.create_task(self._ws.close())
            self._ws = None
            self._last_mode = None
            self._last_freq = None


    # This function will be running in a separate thread and updates self._last_mode and self._last_freq
    async def listen(self):
        if not self._ws:
            logger.error('SDR Connect is not connected')
            return
        logger.info('listening from SdrConnect')
        try:
            async for message in self._ws:
                if self._listen_task is None:
                    return
                response = json.loads(message)
                if response['event_type'] == 'property_changed':
                    if response['property'] == FREQUENCY_PROPERTY:
                        self._last_freq = int(response['value'])
                    elif response['property'] == MODE_PROPERTY:
                        native_mode = response['value']
                        self._last_mode = native_mode
        except Exception as e:
            logger.error(e)
            self._ws = None


    async def set_freq_mode(self, freq: int, mode: CoreMode) -> None:
        if not self._ws:
            raise ConnectionResetError('SDR Connect is disconnected')

        command = set_frequency_message(freq)
        await self._ws.send(command)
        self._last_freq = freq

        native_mode = self._mapper.get_native_mode(mode)
        if self._last_mode != native_mode:
            command = set_mode_message(native_mode)
            await self._ws.send(command)
            self._last_mode = native_mode


    async def get_freq(self) -> int:
        if not self._ws:
            raise ConnectionResetError('SDR Connect is disconnected')
        if not self._last_freq:
            raise Exception('SDR Connect Frequency not available')
        return self._last_freq

    async def get_mode(self) -> CoreMode:
        if not self._ws:
            raise ConnectionResetError('SDR Connect is disconnected')
        if not self._last_mode:
            raise Exception('SDR Connect Mode not available')
        return self._mapper.get_core_mode(self._last_mode)

    async def _query_device_frequency(self) -> int | None:
        new_freq = await self._query_device_property(FREQUENCY_PROPERTY)
        if new_freq is not None:
            self._last_freq = int(new_freq)
        return self._last_freq

    async def _query_device_mode(self) -> str | None:
        new_mode = await self._query_device_property(MODE_PROPERTY)
        if new_mode is not None:
            self._last_mode = new_mode
        return self._last_mode

    async def _query_device_property(self, prop: str) -> str | None:
        logger.info(f'querying device property: {prop}')
        if not self._ws:
            logger.error('SDR Connect is not connected')
            return None
        if prop == FREQUENCY_PROPERTY:
            command = get_frequency_message()
        elif prop == MODE_PROPERTY:
            command = get_mode_message()
        else:
            logger.error(f'Invalid property: {prop}')
            return None
        await self._ws.send(command)
        while True:
            response = json.loads(await self._ws.recv())
            if response['event_type'] == 'get_property_response' and response['property'] == prop:
                new_value = response['value']
                return new_value
            else:
                logger.info(f'ignored event: event_type: {response["event_type"]}, property: {response["property"]}')
