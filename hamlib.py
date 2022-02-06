import re
import socket

BUFFER_SIZE = 1024


def parse_frequency(message):
    result = re.match(r"b\'(\d+)\\n\'", message)
    if result:
        freq_str = result.group(1)
        if freq_str:
            return int(freq_str)

def parse_mode(message):
    result = re.match(r"b\'(\w+)\\", message)
    if result:
        freq_str = result.group(1)
        if freq_str:
            return freq_str

class HamLibClient:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def __enter__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.ip, self.port))
        return self

    def set_freq(self, freq):
        message = f'F {freq}\n'
        self.sock.send(bytes(message, 'utf-8'))
        result = str(self.sock.recv(BUFFER_SIZE))
        if result == 'RPRT 0\n':
            return True
        else:
            return False

    def get_freq(self):
        message = f'f\n'
        self.sock.send(bytes(message, 'utf-8'))
        message = str(self.sock.recv(BUFFER_SIZE))
        return parse_frequency(message)

    def get_mode(self):
        message = f'm\n'
        self.sock.send(bytes(message, 'utf-8'))
        message = str(self.sock.recv(BUFFER_SIZE))
        return parse_mode(message)

    def close(self):
        if self.sock:
            self.sock.close()
            self.sock = None

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
