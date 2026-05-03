# This module defines the Client protocol that all CatRelay client modules must implement
from typing import Protocol, runtime_checkable
from enum import Enum

class CoreMode(Enum):
    # All clients should support these core modes
    # Modes in all function parameters and returns are core modes
    # Client can decide if native device modes are stored or not, but should always return the core mode
    # Client should only store last set core mode and never set device mode if mode is the same as the last mode to avoid overwriting device's native mode
    FM = 'FM'
    AM = 'AM'
    USB = 'USB'
    LSB = 'LSB'
    CW = 'CW'

@runtime_checkable
class Client(Protocol):

    def __enter__(self) -> 'Client':
        '''
        Enter the context of the client. Connect your device here.
        '''
        ...
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        '''
        Exit the context of the client. Clean up any resources here.
        '''
        ...

    def close(self) -> None:
        '''
        Close the client and disconnect your device here.
        '''
        ...
    
    def get_new_freq(self) -> int | None:
        '''
        Get the new frequency from the device. None if no change
        '''
        ...
    
    def get_new_mode(self) -> CoreMode | None:
        '''
        Get the new mode from the device. None if no change
        Should only return the core mode, not the native mode
        '''
        ...
    
    def set_freq_mode(self, freq: int | None, mode: CoreMode | None) -> None:
        '''
        Set the frequency and mode on the device.
        Expect the mode parameter to be a core mode, not the native mode
        '''
        ...