import socket

BUFFER_SIZE = 1024


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

    def close(self):
        if self.sock:
            self.sock.close()
            self.sock = None

    def __exit__(self, exception_type, exception_value, traceback):
        self.close()
