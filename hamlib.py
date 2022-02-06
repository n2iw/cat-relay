import re
import socket

BUFFER_SIZE = 1024


def parse_frequency(message):
    result = re.match(r"b\'(\d+)\\n\'", str(message))
    if result:
        freq_str = result.group(1)
        if freq_str:
            return int(freq_str)


def parse_mode(message):
    result = re.match(r"b\'(\w+)\\", str(message))
    if result:
        freq_str = result.group(1)
        if freq_str:
            return freq_str


def parse_result(message):
    result = re.match(r"b\'RPRT +(\d)\\n\'", str(message))
    if result:
        succeeded = result.group(1)
        return succeeded == '0'


class HamLibClient:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.current_mode = ''

    def __enter__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.ip, self.port))
        return self

    def send(self, message):
        self.sock.send(bytes(message, 'utf-8'))

    def receive(self):
        return str(self.sock.recv(BUFFER_SIZE))

    def set_freq(self, freq, mode=None):
        if self.current_mode != mode and mode is not None:
            message = f'M {mode} -1\n'
            self.send(message)
            result = self.receive()
            if parse_result(result):
                self.current_mode = mode
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

    def close(self):
        if self.sock:
            self.sock.close()
            self.sock = None

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
