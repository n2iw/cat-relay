import socket
import threading

from .radio_info import get_radio_info, set_frequency_message


def parse_frequency_mode(data):
    info = get_radio_info(data)
    if info:
        freq = info.get_frequency()
        mode = map_mode(info.get_mode(), freq)
        return freq, mode
    else:
        return None


# Map 'SSB' to 'USB' or 'LSB' base on frequency
# 'RTTY' to 'USB'
def map_mode(mode, freq):
    if mode == 'SSB':
        return 'USB' if freq > 10_000_000 else 'LSB'
    elif mode == 'RTTY':
        return 'USB'
    return mode


class N1MMClient:
    def __init__(self, listen_port, send_ip, send_port):
        self.listen_port = listen_port
        self.send_ip = send_ip
        self.send_port = send_port
        self.listen_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.last_mode = ''
        self.last_freq = 0
        self.terminated = False # flag to terminate the thread

    def __enter__(self):
        self.listen_sock.bind(('0.0.0.0', self.listen_port))
        self.thread = threading.Thread(target=self.listen)
        self.thread.start()
        return self

    # This function will be running in a separate thread and updates self.last_mode and self.last_freq
    def listen(self):
        print(f'listening UDP in a new thread')
        while True:
            if self.terminated:
                print(f'Terminated flag detected, terminate the thread')
                return
            data = self.receive()
            freq, mode = parse_frequency_mode(data)
            if freq:
                self.last_freq = freq
                self.last_mode = mode

    def send(self, message):
        if isinstance(message, str):
            b_msg = bytes(message, 'utf-8')
        else:
            b_msg = message
        self.send_sock.sendto(b_msg, (self.send_ip,  self.send_port))

    def receive(self):
        data, addr = self.listen_sock.recvfrom(1024)  # buffer size is 1024 bytes
        return data

    def close(self):
        self.terminated = True
        self.thread.join()
        if self.listen_sock:
            self.listen_sock.close()
            self.listen_sock = None
        if self.send_sock:
            self.send_sock.close()
            self.send_sock = None

    def get_last_mode(self):
        return self.last_mode

    def get_last_freq(self):
        return self.last_freq

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def get_freq(self):
        return self.last_freq

    def get_mode(self):
        return self.last_mode

    # set frequency only, mode is not supported in N1MM
    def set_freq_mode(self, freq, mode=None):
        print(f'Set freq: {freq}, mode: {mode}')
        cmd = set_frequency_message(freq)
        if cmd:
            self.last_freq = freq
            self.send(cmd)

