import logging
import xmlrpc.client
from requests.exceptions import ConnectionError
from utils.cat_client import CATClient
from utils.client import CoreMode

from .transport import RequestsTransport

logger = logging.getLogger(__name__)


def _int_from_xmlrpc(v: object) -> int:
    """Coerce XML-RPC values (typed as _Marshallable) to int."""
    if isinstance(v, (bytes, bytearray)):
        s = v.decode("ascii", errors="replace").strip()
        return int(float(s))
    if isinstance(v, str):
        return int(float(v))
    if isinstance(v, (int, float)):
        return int(v)
    raise TypeError(f"unexpected VFO type from flrig: {type(v)!r}")

## The following are the valid modes that can be used on my Icom IC-7100. They may require changing for
## your radio. Note that we use two dictionaries here: RADIO_TO_SDR converts the string we get from the
## transceiver to the mode that the SDR can understand. SDR_TO_RADIO converts the SDR string to what the
## radio wants.

## Note that if you want to focus on voice modes, you should probably translate "USB" to "USB"
## instead of "USB" to "USB-D" because USB-D is meant for digital decoding and may mute the rig microphone,
## depending on how you have your USB connection set on the radio. The same is true for "LSB" and "AM" modes.


class FlrigClient(CATClient):
    NATIVE_TO_CORE_MODES = {
        'AM':CoreMode.AM,
        'AM-D':CoreMode.AM,
        'AM-N':CoreMode.AM,
        'CW':CoreMode.CW,
        'CW-L':CoreMode.CW,
        'CW-R':CoreMode.CW,
        'CW-U':CoreMode.CW,
        'DATA-FM':CoreMode.FM,
        'DATA-FMN':CoreMode.FM,
        'DATA-L':CoreMode.LSB,
        'DATA-U':CoreMode.USB,
        'DV':CoreMode.FM,
        'FM':CoreMode.FM,
        'FM-D':CoreMode.FM,
        'FM-N':CoreMode.FM,
        'FSK':CoreMode.USB,
        'LSB':CoreMode.LSB,
        'LSB-D':CoreMode.LSB,
        'PSK':CoreMode.USB,
        'RTTY':CoreMode.USB,
        'RTTY-L':CoreMode.LSB,
        'RTTY-R':CoreMode.LSB,
        'RTTY-U':CoreMode.USB,
        'USB':CoreMode.USB,
        'USB-D':CoreMode.USB,
        'WFM':CoreMode.FM,
    }

    CORE_TO_NATIVE_MODES = {
    }

    def __init__(self, ip, port):
        self._ip = ip
        self._port = port
        self._last_mode = None
        self._last_freq = None
        self._flrig: xmlrpc.client.ServerProxy | None = None

    def open(self) -> None:
        try:
            self.flrig = xmlrpc.client.ServerProxy('http://{}:{}/'.format(self._ip, self._port), transport=RequestsTransport(use_builtin_types=True), allow_none=True)
            super().open()
        except ConnectionError as e:
            logger.error('%s', e)
            logger.error('Are you sure flrig is running?')

    def close(self) -> None:
        if self._flrig:
            self._flrig.close()
            self._flrig = None

    def set_freq_mode(self, freq: int | None, mode: CoreMode | None = None) -> None:
        if not self.flrig:
            logger.error('Flrig is not connected')
            return

        if freq is not None:
            if self._last_freq != freq:
                self.flrig.rig.set_frequency(float(freq))
                self._last_freq = freq

        if not mode:
            logger.error('Mode is not set')
            return
        native_mode = self.core_to_native_mode(mode)
        if not native_mode in self.NATIVE_TO_CORE_MODES.keys():
            logger.warning(f'Unmapped Core Mode: {native_mode}')
            return None
        if self._last_mode != native_mode:
            self.flrig.rig.set_mode(native_mode)
            self._last_mode = native_mode

    def get_freq(self) -> int | None:
        if not self.flrig:
            logger.error('Flrig is not connected')
            return None
        raw = self.flrig.rig.get_vfo()
        if raw is None:
            logger.error('Failed to get frequency from Flrig')
            return None
        freq = _int_from_xmlrpc(raw)
        return freq

    def get_mode(self) -> str | None:
        if not self.flrig:
            logger.error('Flrig is not connected')
            return None
        raw = self.flrig.rig.get_mode()
        if raw is None:
            logger.error('Failed to get mode from Flrig')
            return None
        native_mode = str(raw)
        return native_mode

    def get_native_to_core_mode_mapping(self) -> dict[str, CoreMode]:
        return self.NATIVE_TO_CORE_MODES
    
    def get_core_to_native_mode_mapping(self) -> dict[CoreMode, str]:
        return self.CORE_TO_NATIVE_MODES