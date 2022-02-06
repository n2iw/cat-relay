import re
import socket

BUFFER_SIZE = 1024


class TCPClient:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.last_mode = ''
        self.last_freq = 0

    def __enter__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.ip, self.port))
        self.last_freq = self.get_freq()
        self.last_mode = self.get_mode()
        return self

    def send(self, message):
        self.sock.send(bytes(message, 'utf-8'))

    def receive(self):
        msg = str(self.sock.recv(BUFFER_SIZE))
        result = re.match(r"b\'(.+)\'", str(msg))
        if result:
            return result.group(1)

    def close(self):
        if self.sock:
            self.sock.close()
            self.sock = None

    def get_last_mode(self):
        return self.last_mode

    def get_last_freq(self):
        return self.last_freq

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
