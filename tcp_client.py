import re
import socket

BUFFER_SIZE = 1024


class TCPClient:
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
        msg = str(self.sock.recv(BUFFER_SIZE))
        result = re.match(r"b\'(.+)\'", str(msg))
        if result:
            return result.group(1)

    def close(self):
        if self.sock:
            self.sock.close()
            self.sock = None

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
