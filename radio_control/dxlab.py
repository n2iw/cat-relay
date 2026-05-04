import re
import logging
from utils.cat_client import CATClient
from utils.client import CoreMode
from utils.tcp_client import TCPClient

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

class Commander(CATClient):
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

    def open(self) -> None:
        self._tcp = TCPClient(self._ip, self._port)
        self._tcp.open()
        super().open()

    def close(self) -> None:
        if self._tcp:
            self._tcp.close()
            self._tcp = None

    def get_native_to_core_mode_mapping(self) -> dict[str, CoreMode]:
        return self.NATIVE_TO_CORE_MODES

    def get_core_to_native_mode_mapping(self) -> dict[CoreMode, str]:
        return self.CORE_TO_NATIVE_MODES

    def get_freq(self) -> int | None:
        if not self._tcp:
            logger.error('DXLab is not connected')
            return None
        cmd = format_command('command', 'CmdGetFreq') + format_command('parameters')
        self._tcp.send(cmd)
        return parse_frequency(self._tcp.receive())

    def get_mode(self) -> str | None:
        if not self._tcp:
            logger.error('DXLab is not connected')
            return None
        cmd = format_command('command', 'CmdSendMode') + format_command('parameters')
        self._tcp.send(cmd)
        return parse_mode(self._tcp.receive())

    def set_freq_mode(self, freq: int | None, mode: CoreMode | None = None) -> None:
        if not self._tcp:
            logger.error('DXLab is not connected')
            return
        frequency = freq if freq is not None else self.get_last_freq()
        if frequency is None:
            logger.error('Frequency is not set')
            return
        if not mode:
            logger.error('Mode is not set')
            return
        native_mode = self.core_to_native_mode(mode)

        if mode and self.get_last_mode() != mode:
            parameters = format_command('xcvrfreq', format_freq(frequency)) + format_command('xcvrmode', native_mode)
            cmd = format_command('command', 'CmdSetFreqMode') + format_command('parameters', parameters)
        elif frequency and self.get_last_freq() != frequency:
            parameters = format_command('xcvrfreq', format_freq(frequency))
            cmd = format_command('command', 'CmdSetFreq') + format_command('parameters', parameters)
        else:
            return
        self._tcp.send(cmd)
        if mode:
            self.set_last_mode(mode)
        self.set_last_freq(frequency)
