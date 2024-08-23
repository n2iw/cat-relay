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


def format_freq(freq):
    # return f'{freq/1000:,.3f}'
    # has to add leading 0s to make MacLogger DX work, DXlab and RUMlogNG don't need it
    return f'{freq/1000:>010,.3f}'




VALID_MODES = [
    'AM',
    'CW',
    'CW-R',
    'DATA-L',
    'DATA-U',
    'FM',
    'LSB',
    'RTTY',
    'RTTY-R',
    'USB',
    'WBFM'
]


class Commander(CATClient):
    def get_freq(self):
        cmd = format_command('command', 'CmdGetFreq') + format_command('parameters')
        self.send(cmd)
        self.set_last_freq(parse_frequency(self.receive()))
        return self.get_last_freq()

    def get_mode(self):
        cmd = format_command('command', 'CmdSendMode') + format_command('parameters')
        self.send(cmd)
        mode = self.map_mode(parse_mode(self.receive()))
        if mode:
            self.set_last_mode(mode)
        return self.get_last_mode()

    def set_freq_mode(self, freq, mode=None):
        if mode and self.get_last_mode() != mode:
            parameters = format_command('xcvrfreq', format_freq(freq)) + format_command('xcvrmode', mode)
            cmd = format_command('command', 'CmdSetFreqMode') + format_command('parameters', parameters)
        elif freq and self.get_last_freq() != freq:
            parameters = format_command('xcvrfreq', format_freq(freq))
            cmd = format_command('command', 'CmdSetFreq') + format_command('parameters', parameters)
        else:
            return
        self.send(cmd)
        self.set_last_mode(mode)
        self.set_last_freq(freq)
