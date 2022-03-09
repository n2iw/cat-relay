import time
import xmlrpc.client
from transport import RequestsTransport

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

class FlrigClient():

    def __init__(self, ip, port):
        self.last_mode = None
        self.last_freq = None
        self._ip = ip
        self._port = port
        self._sock = None
        self.flrig = xmlrpc.client.ServerProxy('http://{}:{}/'.format(self._ip, self._port), transport=RequestsTransport(use_builtin_types=True), allow_none=True)
        print(f'init: flrig = {self.flrig}')

    def __enter__(self):
#        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#        self._sock.connect((self._ip, self._port))
#        self._enter()
        print(f'Attempting to connect to connect to Flrig at IP address={self._ip}, port={self._port}, via XMP-RPC')
        print(f'enter: flrig = {self.flrig}')
        return self

    def __exit__(self, a, b, c):
        print(f'exit')


    def set_freq_mode(self, raw_freq, mode):
        freq = float(raw_freq)
        print(f'set_freq_mode({raw_freq}, {mode}')
        if freq and self.last_freq != freq:
            self.flrig.rig.set_frequency(freq)
            self.last_freq = freq

        if mode and self.last_mode != mode:
            radiomode = mode
            if (mode == "USB"):
                radiomode = "USB-D"
            if (mode == "LSB"):
                radiomode = "LSB-D"
            self.flrig.rig.set_mode(radiomode)
            self.last_mode = mode


    def get_last_freq(self):
        return int(self.last_freq)

    def get_last_mode(self):
        return self.last_mode

    def get_freq(self):
        self.last_freq = self.flrig.rig.get_vfo()
        return int(self.last_freq)

    def get_mode(self):
        radiomode = self.flrig.rig.get_mode()
        sdrmode = radiomode
        if (radiomode == "USB-D"):
                sdrmode = "USB"
        if (radiomode == "LSB-D"):
                sdrmode = "LSB"
        self.last_mode = sdrmode
        return self.get_last_mode()
