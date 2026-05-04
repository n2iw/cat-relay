from abc import abstractmethod
from utils.client import CoreMode, Client
import logging

logger = logging.getLogger(__name__)

class CATClient(Client):

    @abstractmethod
    def get_native_to_core_mode_mapping(self) -> dict[str, CoreMode]:
        '''
        :return: dictionary of modes mapping from native mode to core mode
        if a native mode matches core mode, it's ok to don't include it in the mapping
        subclass should implement this method
        '''
        pass

    @abstractmethod
    def get_core_to_native_mode_mapping(self) -> dict[CoreMode, str]:
        '''
        :return: dictionary of modes mapping from core mode to native mode
        if a core mode matches native mode, it's ok to don't include it in the mapping
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
        '''
        This method should set the frequency and mode on the device.
        :param freq: frequency in Hz, None if not available
        :param mode: core mode, None if not available
        subclass should implement this method
        '''
        pass

    DEFAULT_CORE_MODE_MAPPING = {
        'FM': CoreMode.FM,
        'AM': CoreMode.AM,
        'USB': CoreMode.USB,
        'LSB': CoreMode.LSB,
        'CW': CoreMode.CW
    }

    DEFAULT_NATIVE_MODE_MAPPING = {
        CoreMode.FM: 'FM',
        CoreMode.AM: 'AM',
        CoreMode.USB: 'USB',
        CoreMode.LSB: 'LSB',
        CoreMode.CW: 'CW'
    }

    def __init__(self, ip, port):
        self._last_mode_reported: CoreMode | None = None
        self._last_freq_reported: int | None = None

    def get_new_freq(self) -> int | None:
        '''
        :return: new frequency in Hz if it has changed since last time it was stored in self._last_freq_reported
        '''
        freq = self.get_freq()
        if freq and freq != self._last_freq_reported:
            self._last_freq_reported = freq
            return freq
        return None
    
    def get_new_mode(self) -> CoreMode | None:
        '''
        :return: new core mode if it has changed since last time it was stored in self._last_mode_reported
        '''
        native_mode = self.get_mode()
        if not native_mode:
            logger.error('Failed to get mode from device')
            return None
        mode = self.native_to_core_mode(native_mode)
        if not mode:
            logger.error('Unmapped native mode: %s', native_mode)
            return None
        if mode != self._last_mode_reported:
            self._last_mode_reported = mode
            return mode
        return None

    def open(self):
        new_freq = self.get_new_freq()
        if new_freq is not None:
            self._last_freq_reported = new_freq
        new_mode = self.get_new_mode()
        if new_mode is not None:
            self._last_mode_reported = new_mode

    def native_to_core_mode(self, mode: str) -> CoreMode | None:
        '''
        :param mode: native mode from the device 
        :return: equivalent core mode
        if mode is not in the mapping, return mode itself
        '''
        alternative_modes = self.DEFAULT_CORE_MODE_MAPPING | self.get_native_to_core_mode_mapping() 
        return  alternative_modes.get(mode) 
    
    def core_to_native_mode(self, mode: CoreMode) -> str:
        '''
        :param mode: core mode
        :return: equivalent native mode
        if mode is not in the mapping, return mode itself
        '''
        alternative_modes = self.DEFAULT_NATIVE_MODE_MAPPING | self.get_core_to_native_mode_mapping() 
        return alternative_modes.get(mode) or mode.value

    def get_last_freq(self) -> int | None:
        return self._last_freq_reported
    
    def get_last_mode(self) -> CoreMode | None:
        return self._last_mode_reported
    
    def set_last_freq(self, freq: int | None) -> None:
        self._last_freq_reported = freq
    
    def set_last_mode(self, mode: CoreMode | None) -> None:
        self._last_mode_reported = mode