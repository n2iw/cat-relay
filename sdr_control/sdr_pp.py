## This module is a client for the SDR++ app

## It is a lightweight substitute for a full Hamlib implementation

## As mentioned in the README file, this would probably work with pretty much any SDR
## software that implements the f, m, F, and M Hamlib functions that 
## read and write the frequency and mode.

import logging
import re
from utils.client import CoreMode
from utils.mode_mapper import ModeMapper
from utils.tcp_client import TCPClient
from utils.client import Client

logger = logging.getLogger(__name__)


def parse_frequency(message) -> int | None:
    result = re.match(r"(\d+)\\n", str(message))
    if result:
        freq_str = result.group(1)
        if freq_str:
            return int(freq_str)
    return None


def parse_mode(message) -> str | None:
    result = re.match(r"(\w+)\\", str(message))
    if result:
        freq_str = result.group(1)
        if freq_str:
            return freq_str
    return None


def parse_result(message) -> bool:
    result = re.match(r"RPRT +(\d)\\n", str(message))
    if result:
        succeeded = result.group(1)
        return succeeded == '0'
    return False




'''
# Valid modes for Hamlib
HAMLIB_VALID_MODES = [
    'AM',
    'AMS',
    'CW',
    'CWR',
    'DSB'
    'ECSSLSB',
    'ECSSUSB',
    'FA',
    'FM',
    'LSB',
    'PKTFM',
    'PKTLSB',
    'PKTUSB',
    'RTTY',
    'RTTYR',
    'SAH',
    'SAL',
    'SAM',
    'USB',
    'WFM',
]

#Valid modes for SDR++
SDRPP_VALID_MODES = [
    'WFM',
    'FM',
    'AM',
    'USB',
    'LSB',
    'DSB',
    'CW',
    'RAW'
]

'''



class SdrPPClient(Client):

    NATIVE_TO_CORE_MODES = {
        'WFM': CoreMode.FM,  # WFM mode from SDR Connect will be converted to WFM mode
        'DSB': CoreMode.AM,  # DSB mode from SDR Connect will be converted to AM mode
    }

    CORE_TO_NATIVE_MODES = {
    }

    def __init__(self, ip, port):
        self._ip = ip
        self._port = port
        self._tcp: TCPClient | None = None
        self._mapper = ModeMapper(self.CORE_TO_NATIVE_MODES, self.NATIVE_TO_CORE_MODES)

    async def __aenter__(self) -> 'SdrPPClient':
        self._tcp = TCPClient(self._ip, self._port)
        if not self._tcp:
            raise Exception('Failed to connect to SDR++')
        await self._tcp.open()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._tcp:
            await self._tcp.close()
            self._tcp = None

    async def set_freq_mode(self, freq: int, mode: CoreMode) -> None:
        if not self._tcp:
            logger.error('SDR++ is not connected')
            return
        if await self.get_mode() != mode:
            native_mode = self._mapper.get_native_mode(mode)
            message = f'M {native_mode} -1\n'
            await self._tcp.send(message)
            result = await self._tcp.receive()
            if not parse_result(result):
                logger.error('Set SDR++ to %s mode failed!', mode)

        if await self.get_freq() != freq:
            message = f'F {freq}\n'
            await self._tcp.send(message)
            result = await self._tcp.receive()
            if not parse_result(result):
                logger.error('Set SDR++ to %s Hz failed!', freq)

    async def get_freq(self) -> int:
        if not self._tcp:
            raise Exception('SDR++ is not connected')
        message = f'f\n'
        await self._tcp.send(message)
        freq = parse_frequency(await self._tcp.receive())
        if freq is None:
            raise Exception('Failed to get frequency from SDR++')
        return freq

    async def get_mode(self) -> CoreMode:
        if not self._tcp:
            raise Exception('SDR++ is not connected')
        message = f'm\n'
        await self._tcp.send(message)
        mode = parse_mode(await self._tcp.receive())
        if mode is None:
            raise Exception('Failed to get mode from SDR++')
        return self._mapper.get_core_mode(mode)