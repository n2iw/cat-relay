from utils.tcp_client import TCPClient
from abc import abstractmethod
from utils.client import CoreMode

class CATClient(TCPClient):

    @abstractmethod
    def get_native_to_core_mode_mapping(self) -> dict[str, str]:
        '''
        :return: dictionary of modes mapping from native mode to core mode
        if a native mode matches core mode, it's ok to don't include it in the mapping
        subclass should implement this method
        '''
        pass

    @abstractmethod
    def get_freq(self) -> int | None:
        '''
        :return: current frequency on the device in Hz, None if not available
        subclass should implement this method
        '''
        pass

    @abstractmethod
    def get_mode(self) -> str | None:
        '''
        :return: current mode on the device, None if not available, 
        subclass should implement this method
        '''
        pass

    @abstractmethod
    def set_freq_mode(self, freq: int | None, mode: CoreMode | None) -> None:
        pass

    def __init__(self, ip, port):
        super().__init__(ip, port)
        self._last_mode = ''
        self._last_freq = 0

    def get_new_freq(self) -> int | None:
        '''
        :return: new frequency in Hz if it has changed since last time it was stored in self._last_freq
        '''
        freq = self.get_freq()
        if freq and freq != self.get_last_freq():
            self.set_last_freq(freq)
            return freq
        return None
    
    def get_new_mode(self) -> CoreMode | None:
        '''
        :return: new core mode if it has changed since last time it was stored in self._last_mode
        '''
        native_mode = self.get_mode()
        mode = self.native_to_core_mode(native_mode, native_mode)
        if mode and mode != self.get_last_mode():
            self.set_last_mode(mode)
            return mode
        return None

    def _enter(self):
        new_freq = self.get_new_freq()
        if new_freq is not None:
            self._last_freq = new_freq
        new_mode = self.get_new_mode()
        if new_mode is not None:
            self._last_mode = new_mode

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

    def native_to_core_mode(self, mode: str | None) -> str | None:
        '''
        :param mode: native mode from the device 
        :return: equivalent core mode
        if mode is not in the mapping, return mode itself
        '''
        if mode:
            alternative_modes = self.get_native_to_core_mode_mapping()
            return alternative_modes.get(mode, mode)

        return None