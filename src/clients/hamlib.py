## This module is a client for the Hamlib/rigctld apps, for example, SDR++ and QLog

## It is a lightweight substitute for a full Hamlib implementation

## As mentioned in the README file, this would probably work with pretty much any SDR or Logging
## software that implements the f, m, F, and M Hamlib functions that 
## read and write the frequency and mode.

import logging
import re
from clients.base_client import CoreMode, DataNotAvailableException, BaseClient
from clients.utils.mode_mapper import ModeMapper
from clients.utils.tcp_client import TCPClient

logger = logging.getLogger(__name__)


def parse_frequency(message) -> int | None:
    result = re.match(r"(\d+)\\n", str(message))
    if result:
        freq_str = result.group(1)
        if freq_str:
            return int(freq_str)
    return None


def parse_mode(message) -> str | None:
    result = re.match(r"([\w-]+)\\", str(message))
    if result:
        freq_str = result.group(1)
        if freq_str:
            return freq_str
    logger.error(f'Failed to parse mode from {message}')
    return None


def parse_result(message) -> bool:
    result = re.match(r"RPRT +(\d)\\n", str(message))
    if result:
        succeeded = result.group(1)
        return succeeded == '0'
    return False


class HamlibClient(BaseClient):

    NATIVE_TO_CORE_MODES = {
        'WFM': CoreMode.FM,  # WFM mode from SDR Connect will be converted to WFM mode
        'DSB': CoreMode.AM,  # DSB mode from SDR Connect will be converted to AM mode
        'RAW': CoreMode.NOT_SUPPORTED,
        'SAM': CoreMode.AM,
        'PKTUSB': CoreMode.USB,
        'CWR': CoreMode.CW,
        'RTTY': CoreMode.USB,
        'RTTYR': CoreMode.LSB,
        'ECSSLSB': CoreMode.LSB,
        'ECSSUSB': CoreMode.USB,
        'PKTFM': CoreMode.FM,
        'PKTLSB': CoreMode.LSB,
        'SAH': CoreMode.AM,
        'SAL': CoreMode.LSB,
        'AM-D': CoreMode.AM,
        'FM-D': CoreMode.FM,
        'AMS': CoreMode.NOT_SUPPORTED,
        'FA': CoreMode.NOT_SUPPORTED
    }

    CORE_TO_NATIVE_MODES = {
    }

    def __init__(self, ip: str, port: int, name: str = 'SDR++'):
        self._ip = ip
        self._port = port
        self.name = name
        self._tcp: TCPClient | None = None
        self._mapper = ModeMapper(self.CORE_TO_NATIVE_MODES, self.NATIVE_TO_CORE_MODES)

    async def __aenter__(self) -> 'HamlibClient':
        self._tcp = TCPClient(self._ip, self._port)
        if not self._tcp:
            raise Exception(f'Failed to connect to {self.name}')
        await self._tcp.open()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._tcp:
            await self._tcp.close()
            self._tcp = None

    async def set_freq_mode(self, freq: int, mode: CoreMode) -> None:
        if not self._tcp:
            logger.error(f'{self.name} is not connected')
            return
        if await self.get_mode() != mode:
            native_mode = self._mapper.get_native_mode(mode)
            message = f'M {native_mode} -1\n'
            await self._tcp.send(message)
            result = await self._tcp.receive()
            if not parse_result(result):
                logger.error(f'Set {self.name} to {mode} mode failed!')

        if await self.get_freq() != freq:
            message = f'F {freq}\n'
            await self._tcp.send(message)
            result = await self._tcp.receive()
            if not parse_result(result):
                logger.error(f'Set {self.name} to {freq} Hz failed!')

    async def get_freq(self) -> int:
        if not self._tcp:
            raise Exception(f'{self.name} is not connected')
        message = f'f\n'
        await self._tcp.send(message)
        freq = parse_frequency(await self._tcp.receive())
        if freq is None:
            raise DataNotAvailableException(f'Failed to get frequency from {self.name}')
        return freq

    async def get_mode(self) -> CoreMode:
        if not self._tcp:
            raise Exception(f'{self.name} is not connected')
        message = f'm\n'
        await self._tcp.send(message)
        mode = parse_mode(await self._tcp.receive())
        if mode is None:
            raise DataNotAvailableException(f'Failed to get mode from {self.name}')
        return self._mapper.get_core_mode(mode)