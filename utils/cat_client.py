from utils.tcp_client import TCPClient

class CATClient(TCPClient):
    ALTERNATIVE_MODES = {
        'RTTY': 'USB',  # RTTY mode from radio will be mapped to USB mode
        'WFM': 'FM',  # WFM mode from SDR++ will be mapped to FM mode
        'RAW': None,  # RAW mode from SDR++ will be disabled
        'DSB': None  # DSB mode from SDR++ will be disabled
    }

    def __init__(self, ip, port):
        super().__init__(ip, port)
        self._last_mode = ''
        self._last_freq = 0

    def _enter(self):
        self._last_freq = self.get_freq()
        self._last_mode = self.get_mode()

    def map_mode(self, mode):
        valid_mode = mode
        if mode in self.ALTERNATIVE_MODES:
            valid_mode = self.ALTERNATIVE_MODES[mode]

        return valid_mode

    def set_last_mode(self, mode):
        if mode:
            self._last_mode = mode

    def get_last_mode(self):
        return self._last_mode

    def set_last_freq(self, freq):
        if freq and isinstance(freq, int):
            self._last_freq = freq

    def get_last_freq(self):
        return self._last_freq
