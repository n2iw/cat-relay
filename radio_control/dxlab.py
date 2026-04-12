import re

from utils.cat_client import CATClient


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




MAP_MODES = {
    'AM': 'AM',
    'CW': 'CW',
    'CW-R': 'CW',
    'DATA-L': 'LSB',
    'DATA-U': 'USB',
    'FM': 'FM',
    'LSB': 'LSB',
    'RTTY': 'USB',
    'RTTY-R': 'LSB',
    'USB': 'USB',
    'WBFM': 'WFM'
}


class Commander(CATClient):
    def get_new_freq(self) -> int | None:
        cmd = format_command('command', 'CmdGetFreq') + format_command('parameters')
        self.send(cmd)
        freq = parse_frequency(self.receive())
        if freq and freq != self.get_last_freq():
            self.set_last_freq(freq)
            return freq
        return None

    def get_new_mode(self) -> str | None:
        cmd = format_command('command', 'CmdSendMode') + format_command('parameters')
        self.send(cmd)
        mode = parse_mode(self.receive())
        if mode and mode != self.get_last_mode():
            self.set_last_mode(mode)
            return MAP_MODES.get(mode)
        return None

    def set_freq_mode(self, freq: int | None, mode: str | None = None) -> None:
        frequency = freq if freq is not None else self.get_last_freq()

        if mode and self.get_last_mode() != mode:
            parameters = format_command('xcvrfreq', format_freq(frequency)) + format_command('xcvrmode', mode)
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
