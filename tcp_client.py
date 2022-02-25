import re
import socket

BUFFER_SIZE = 1024


class TCPClient:
    def __init__(self, ip, port):
        self._ip = ip
        self._port = port
        self._sock = None

    def __enter__(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.connect((self._ip, self._port))
        self._enter()
        return self

    def send(self, message):
        self._sock.send(bytes(message, 'utf-8'))

    def receive(self):
        msg = str(self._sock.recv(BUFFER_SIZE))
        result = re.match(r"b\'(.+)\'", str(msg))
        if result:
            return result.group(1)

    def close(self):
        if self._sock:
            self._sock.close()
            self._sock = None

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
