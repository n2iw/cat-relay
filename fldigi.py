import pyfldigi
from tcp_client import TCPClient
import time

VALID_MODES = [
 'LSB',
 'USB',
 'AM',
 'CW',
 'RTTY',
 'FM',
 'WFM',
 'CW-R',
 'RTTY-R',
 'DV',
 'LSB-D',
 'USB-D',
 'AM-D',
 'FM-D'
]

class FldigiClient(TCPClient):

    def __init__(self, ip, port):
        self.last_mode = None
        self.last_freq = None
        self._ip = ip
        self._port = port
        self._sock = None

    def __enter__(self):
#        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#        self._sock.connect((self._ip, self._port))
#        self._enter()
        self.client = pyfldigi.Client(self._ip, self._port)
        return self

    def set_freq_mode(self, raw_freq, mode):
        freq = int(raw_freq)
        if freq and self.last_freq != freq:
            self.client.rig.frequency = freq
            self.last_freq = freq

        if mode and self.last_mode != mode:
            radiomode = mode
            if (mode == "USB"):
                radiomode = "USB-D"
            if (mode == "LSB"):
                radiomode = "LSB-D"
            self.client.rig.mode = radiomode
            self.last_mode = mode


    def get_last_freq(self):
        return int(self.last_freq)

    def get_last_mode(self):
        return self.last_mode

    def get_freq(self):
        self.last_freq = self.client.rig.frequency
        return int(self.get_last_freq())

    def get_mode(self):
        radiomode = self.client.rig.mode
        sdrmode = radiomode
        if (radiomode == "USB-D"):
                sdrmode = "USB"
        if (radiomode == "LSB-D"):
                sdrmode = "LSB"
        self.last_mode = sdrmode
        return self.get_last_mode()
