import re
import logging
from utils.client import CoreMode
from utils.mode_mapper import ModeMapper
from utils.tcp_client import TCPClient
from utils.client import Client

logger = logging.getLogger(__name__)

def format_command(field, children = None):
    if children is None:
        children = ''
    else:
        children = str(children)
    # Make sure every parameter is string
    children_len = len(children)
    field = str(field)
    return f'<{field}:{children_len}>{children}'


def parse_frequency(message):
    result = re.match(r"<CmdFreq:\d+> *([\d,]+\.\d+)", message)
    if result:
        freq_str = result.group(1)
        # remove ',' returned by Commander
        freq_str = freq_str.replace(',', '')
        if freq_str:
            return int(float(freq_str) * 1000)


def parse_mode(message):
    result = re.match(r"<CmdMode:\d+>(\w+)", message)
    if result:
        mode = result.group(1)
        return mode


def format_freq(freq: int) -> str:
    # return f'{freq/1000:,.3f}'
    # has to add leading 0s to make MacLogger DX work, DXlab and RUMlogNG don't need it
    return f'{freq/1000:>010,.3f}'

class Commander(Client):
    NATIVE_TO_CORE_MODES = {
        'CW-R': CoreMode.CW,
        'DATA-L': CoreMode.LSB,
        'DATA-U': CoreMode.USB,
        'RTTY': CoreMode.USB,
        'RTTY-R': CoreMode.LSB,
        'WBFM': CoreMode.FM
    }

    CORE_TO_NATIVE_MODES = {
    }

    def __init__(self, ip, port):
        self._ip = ip
        self._port = port
        self._tcp: TCPClient | None = None
        self._mapper = ModeMapper(self.CORE_TO_NATIVE_MODES, self.NATIVE_TO_CORE_MODES)

    async def __aenter__(self) -> 'Commander':
        self._tcp = TCPClient(self._ip, self._port)
        if self._tcp is None:
            logger.error('DXLab is not connected')
            raise Exception('DXLab is not connected')
        self._tcp.open()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._tcp:
            self._tcp.close()
            self._tcp = None

    async def get_freq(self) -> int:
        if not self._tcp:
            logger.error('DXLab is not connected')
            raise Exception('DXLab is not connected')
        cmd = format_command('command', 'CmdGetFreq') + format_command('parameters')
        self._tcp.send(cmd)
        freq = parse_frequency(self._tcp.receive())
        if freq is None:
            raise Exception('Failed to get frequency from DXLab')
        return freq

    async def get_mode(self) -> CoreMode:
        if not self._tcp:
            logger.error('DXLab is not connected')
            raise Exception('DXLab is not connected')
        cmd = format_command('command', 'CmdSendMode') + format_command('parameters')
        self._tcp.send(cmd)
        mode = parse_mode(self._tcp.receive())
        if mode is None:
            raise Exception('Failed to get mode from DXLab')
        return self._mapper.get_core_mode(mode)

    async def set_freq_mode(self, freq: int, mode: CoreMode) -> None:
        if not self._tcp:
            logger.error('DXLab is not connected')
            return

        if await self.get_mode() != mode:
            native_mode = self._mapper.get_native_mode(mode)
            parameters = format_command('xcvrfreq', format_freq(freq)) + format_command('xcvrmode', native_mode)
            cmd = format_command('command', 'CmdSetFreqMode') + format_command('parameters', parameters)
        elif await self.get_freq() != freq:
            parameters = format_command('xcvrfreq', format_freq(freq))
            cmd = format_command('command', 'CmdSetFreq') + format_command('parameters', parameters)
        else:
            return
        self._tcp.send(cmd)
