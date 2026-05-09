# This module defines the Client protocol that all CatRelay client modules must implement
from typing import Protocol, runtime_checkable
from enum import Enum

class CoreMode(Enum):
    # All clients should support these core modes.
    # Modes in all function parameters and returns are core modes
    # Client can decide if native device modes are stored or not, but should always return the core mode
    # Client should only store the last set core mode and never set device mode
    # if the mode is the same as the last mode to avoid overwriting the device's native mode
    FM = 'FM'
    AM = 'AM'
    USB = 'USB'
    LSB = 'LSB'
    CW = 'CW'
    NOT_SUPPORTED = 'NOT_SUPPORTED'

@runtime_checkable
class Client(Protocol):

    async def __aenter__(self) -> 'Client':
        """
        Open the client and connect your device here.
        """
        ...

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Close the client and disconnect your device here.
        """
        ...
    
    async def get_freq(self) -> int:
        """
        Get the current frequency from the device.
        """
        ...
    
    async def get_mode(self) -> CoreMode:
        """
        Get the current mode from the device.
        Should only return the core mode, not the native mode
        """
        ...
    
    async def set_freq_mode(self, freq: int, mode: CoreMode) -> None:
        """
        Set the frequency and mode on the device.
        Expect the mode parameter to be a core mode, not the native mode
        """
        ...