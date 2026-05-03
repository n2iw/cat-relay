## This module is a client for the SDR++ app

## It is a lightweight substitute for a full Hamlib implementation

## As mentioned in the README file, this would probably work with pretty much any SDR
## software that implements the f, m, F, and M Hamlib functions that 
## read and write the frequency and mode.

import logging
import re
from utils.cat_client import CATClient
from utils.client import CoreMode

logger = logging.getLogger(__name__)


def parse_frequency(message) -> int | None:
    result = re.match(r"(\d+)\\n", str(message))
    if result:
        freq_str = result.group(1)
        if freq_str:
            return int(freq_str)


def parse_mode(message) -> str | None:
    result = re.match(r"(\w+)\\", str(message))
    if result:
        freq_str = result.group(1)
        if freq_str:
            return freq_str


def parse_result(message) -> bool:
    result = re.match(r"RPRT +(\d)\\n", str(message))
    if result:
        succeeded = result.group(1)
        return succeeded == '0'
    return False




'''
# Valid modes for Hamlib
HAMLIB_VALID_MODES = [
    'AM',
    'AMS',
    'CW',
    'CWR',
    'DSB'
    'ECSSLSB',
    'ECSSUSB',
    'FA',
    'FM',
    'LSB',
    'PKTFM',
    'PKTLSB',
    'PKTUSB',
    'RTTY',
    'RTTYR',
    'SAH',
    'SAL',
    'SAM',
    'USB',
    'WFM',
]

#Valid modes for SDR++
SDRPP_VALID_MODES = [
    'WFM',
    'FM',
    'AM',
    'USB',
    'LSB',
    'DSB',
    'CW',
    'RAW'
]

'''



class SdrPPClient(CATClient):

    NATIVE_TO_CORE_MODES = {
        'WFM': 'FM',  # WFM mode from SDR Connect will be converted to WFM mode
        'DSB': 'AM',  # DSB mode from SDR Connect will be converted to AM mode
        'RAW': None  # RAW mode from SDR Connect will be disabled
    }

    CORE_TO_NATIVE_MODES = {
    }

    def set_freq_mode(self, freq: int | None, mode: CoreMode | None = None) -> None:
        if mode and self.get_last_mode() != mode:
            native_mode = self.CORE_TO_NATIVE_MODES.get(mode, mode)
            message = f'M {native_mode} -1\n'
            self.send(message)
            result = self.receive()
            if parse_result(result):
                self.set_last_mode(mode)
            else:
                logger.error('Set Hamlib to %s mode failed!', mode)

        if freq and self.get_last_freq() != freq:
            message = f'F {freq}\n'
            self.send(message)
            result = self.receive()
            if parse_result(result):
                self.set_last_freq(freq)
            else:
                logger.error('Set Hamlib to %s Hz failed!', freq)

    def get_freq(self) -> int | None:
        message = f'f\n'
        self.send(message)
        freq = parse_frequency(self.receive())
        return freq

    def get_mode(self) -> CoreMode | None:
        message = f'm\n'
        self.send(message)
        mode = parse_mode(self.receive()) 
        return mode

    def get_native_to_core_mode_mapping(self) -> dict[str, str]:
        return self.NATIVE_TO_CORE_MODES