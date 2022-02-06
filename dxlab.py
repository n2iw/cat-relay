import re

from tcp_client import TCPClient


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
    result = re.match(r"<CmdFreq:\d+>(\d+.\d+)", message)
    if result:
        freq_str = result.group(1)
        if freq_str:
            return int(float(freq_str) * 1000)


def parse_mode(message):
    result = re.match(r"<CmdMode:\d+>(\w+)", message)
    if result:
        mode = result.group(1)
        return mode


class Commander(TCPClient):
    def get_freq(self):
        cmd = format_command('command', 'CmdGetFreq') + format_command('parameters')
        self.send(cmd)
        self.last_freq = parse_frequency(self.receive())
        return self.last_freq

    def get_mode(self):
        cmd = format_command('command', 'CmdSendMode') + format_command('parameters')
        self.send(cmd)
        self.last_mode = parse_mode(self.receive())
        return self.last_mode

    def set_freq_mode(self, freq, mode=None):
        if self.last_mode != mode and mode is not None:
            self.last_mode = mode
            parameters = format_command('xcvrfreq', freq) + format_command('xcvrmode', mode)
            cmd = format_command('command', 'CmdSetFreqMode') + format_command('parameters', parameters)
        else:
            parameters = format_command('xcvrfreq', freq)
            cmd = format_command('command', 'CmdSetFreq') + format_command('parameters', parameters)
        self.last_freq = freq
        self.send(cmd)
