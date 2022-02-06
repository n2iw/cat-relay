import re
import socket

BUFFER_SIZE = 1024


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
    result = re.match(r"b\'<CmdFreq:\d+>(\d+.\d+)\'", message)
    if result:
        freq_str = result.group(1)
        if freq_str:
            return int(float(freq_str) * 1000)

class Commander:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.current_mode = ''

    def __enter__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.ip, self.port))
        return self

    def get_freq(self):
        cmd = format_command('command', 'CmdGetFreq') + format_command('parameters')
        self.sock.send(bytes(cmd, 'utf-8'))
        message = str(self.sock.recv(BUFFER_SIZE))
        freq = parse_frequency(message)
        return freq

    def set_freq(self, freq, mode=None):
        if self.current_mode != mode and mode is not None:
            self.current_mode = mode
            parameters = format_command('xcvrfreq', freq) + format_command('xcvrmode', mode)
            cmd = format_command('command', 'CmdSetFreqMode') + format_command('parameters', parameters)
        else:
            parameters = format_command('xcvrfreq', freq)
            cmd = format_command('command', 'CmdSetFreq') + format_command('parameters', parameters)
        self.sock.send(bytes(cmd, 'utf-8'))

    def close(self):
        if self.sock:
            self.sock.close()
            self.sock = None

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()