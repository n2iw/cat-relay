from utils.tcp_client import TCPClient
from abc import abstractmethod, ABC

class CATClient(ABC, TCPClient):
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
    
    @abstractmethod
    def get_new_freq(self) -> int | None:
        pass

    @abstractmethod
    def get_new_mode(self) -> str | None:
        pass

    @abstractmethod
    def set_freq_mode(self, freq: int | None, mode: str | None) -> None:
        pass

    def _enter(self):
        new_freq = self.get_new_freq()
        if new_freq is not None:
            self._last_freq = new_freq
        new_mode = self.get_new_mode()
        if new_mode is not None:
            self._last_mode = new_mode

    def map_mode(self, mode):
        valid_mode = mode
        if mode in self.ALTERNATIVE_MODES:
            valid_mode = self.ALTERNATIVE_MODES[mode]

        return valid_mode

    def set_last_mode(self, mode: str) -> None:
        if mode:
            self._last_mode = mode

    def get_last_mode(self) -> str:
        return self._last_mode

    def set_last_freq(self, freq: int) -> None:
        if freq and isinstance(freq, int):
            self._last_freq = freq

    def get_last_freq(self) -> int:
        return self._last_freq
