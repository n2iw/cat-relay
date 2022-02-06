import re
from tcp_client import TCPClient


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


class HamLibClient(TCPClient):

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
            return True
        else:
            return False

    def get_freq(self):
        message = f'f\n'
        self.send(message)
        return parse_frequency(self.receive())

    def get_mode(self):
        message = f'm\n'
        self.send(message)
        return parse_mode(self.receive())