import re

from utils.cat_client import CATClient
from utils.client import CoreMode


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
        'CW-R': 'CW',
        'DATA-L': 'LSB',
        'DATA-U': 'USB',
        'RTTY': 'USB',
        'RTTY-R': 'LSB',
        'WBFM': 'FM'
    }

    CORE_TO_NATIVE_MODES = {
    }

    def get_native_to_core_mode_mapping(self) -> dict[str, str]:
        return self.NATIVE_TO_CORE_MODES

    def get_freq(self) -> int | None:
        cmd = format_command('command', 'CmdGetFreq') + format_command('parameters')
        self.send(cmd)
        return parse_frequency(self.receive())

    def get_mode(self) -> str | None:
        cmd = format_command('command', 'CmdSendMode') + format_command('parameters')
        self.send(cmd)
        return parse_mode(self.receive())

    def set_freq_mode(self, freq: int | None, mode: CoreMode | None = None) -> None:
        frequency = freq if freq is not None else self.get_last_freq()
        native_mode = self.CORE_TO_NATIVE_MODES.get(mode, mode) if mode else None

        if mode and self.get_last_mode() != mode:
            parameters = format_command('xcvrfreq', format_freq(frequency)) + format_command('xcvrmode', native_mode)
            cmd = format_command('command', 'CmdSetFreqMode') + format_command('parameters', parameters)
        elif frequency and self.get_last_freq() != frequency:
            parameters = format_command('xcvrfreq', format_freq(frequency))
            cmd = format_command('command', 'CmdSetFreq') + format_command('parameters', parameters)
        else:
            return
        self.send(cmd)
        if mode:
            self.set_last_mode(mode)
        self.set_last_freq(frequency)
