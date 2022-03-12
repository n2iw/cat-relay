## While not exactly clear from the file name, this module interacts with the SDR++ app

## It is a lightweight substitute for a full Hamlib implementation
## which has many dependences and would be complete overkill for our use.
## It supports only three methods:
##     set_freq_mode, which sets the frequency and mode of the SDR
##     get_freq, which returns the frequency of the SDR
##     get_mode, which returns the mode of the SDR

## As mentioned in the README file, this would probably work with pretty much any SDR
## software that implements the f, m, F, and M Hamlib functions that 
## read and write the frequency and mode.

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
        if mode and self.get_last_mode() != mode:
            message = f'M {mode} -1\n'
            self.send(message)
            result = self.receive()
            if parse_result(result):
                self.set_last_mode(mode)
            else:
                print(f'Set Hamlib to {mode} mode failed!')

        if freq and self.get_last_freq() != freq:
            message = f'F {freq}\n'
            self.send(message)
            result = self.receive()
            if parse_result(result):
                self.set_last_freq(freq)
            else:
                print(f'Set Hamlib to {freq}Hz failed!')

    def get_freq(self):
        message = f'f\n'
        self.send(message)
        self.set_last_freq(parse_frequency(self.receive()))
        return self.get_last_freq()

    def get_mode(self):
        message = f'm\n'
        self.send(message)
        self.set_last_mode(self.map_mode(parse_mode(self.receive())))
        return self.get_last_mode()
