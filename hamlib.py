import re
from cat_client import CATClient


def parse_frequency(message):
    result = re.match(r"(\d+)\\n", str(message))
    if result:
        freq_str = result.group(1)
        if freq_str:
            return int(freq_str)


def parse_mode(message):
    result = re.match(r"(\w+)\\", str(message))
    if result:
        freq_str = result.group(1)
        if freq_str:
            return freq_str


def parse_result(message):
    result = re.match(r"RPRT +(\d)\\n", str(message))
    if result:
        succeeded = result.group(1)
        return succeeded == '0'


VALID_MODES = [
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




class HamLibClient(CATClient):

    def set_freq_mode(self, freq, mode=None):
        if self.last_mode != mode and mode is not None:
            message = f'M {mode} -1\n'
            self.send(message)
            result = self.receive()
            if parse_result(result):
                self.last_mode = mode
            else:
                print(f'Set Hamlib to {mode} mode failed!')

        message = f'F {freq}\n'
        self.send(message)
        result = self.receive()
        if parse_result(result):
            self.last_freq = freq
        else:
            print(f'Set Hamlib to {freq}Hz failed!')

    def get_freq(self):
        message = f'f\n'
        self.send(message)
        self.last_freq = parse_frequency(self.receive())
        return self.last_freq

    def get_mode(self):
        message = f'm\n'
        self.send(message)
        self.last_mode = self.map_mode(parse_mode(self.receive()))
        return self.last_mode
