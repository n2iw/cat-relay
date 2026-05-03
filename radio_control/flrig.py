import logging
import xmlrpc.client
from requests.exceptions import ConnectionError
from utils.client import Client, CoreMode

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


class FlrigClient(Client):
    NATIVE_TO_CORE_MODES = {
        'AM':'AM',
        'AM-D':'AM',
        'AM-N':'AM',
        'CW':'CW',
        'CW-L':'CW',
        'CW-R':'CW',
        'CW-U':'CW',
        'DATA-FM':'FM',
        'DATA-FMN':'FM',
        'DATA-L':'LSB',
        'DATA-U':'USB',
        'DV':'FM',
        'FM':'FM',
        'FM-D':'FM',
        'FM-N':'FM',
        'FSK':'USB',
        'LSB':'LSB',
        'LSB-D':'LSB',
        'PSK':'USB',
        'RTTY':'USB',
        'RTTY-L':'LSB',
        'RTTY-R':'LSB',
        'RTTY-U':'USB',
        'USB':'USB',
        'USB-D':'USB',
        'WFM':'FM'
    }

    CORE_TO_NATIVE_MODES = {
    }

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
#        print(f'Attempting to connect to connect to Flrig at IP address={self._ip}, port={self._port}, via XMP-RPC')
        try:
            self.flrig = xmlrpc.client.ServerProxy('http://{}:{}/'.format(self._ip, self._port), transport=RequestsTransport(use_builtin_types=True), allow_none=True)
        except ConnectionError as e:
            logger.error('%s', e)
            logger.error('Are you sure flrig is running?')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        return

    def close(self):
        self.flrig = None

    def set_freq_mode(self, freq: int | None, mode: CoreMode | None = None) -> None:
        if not self.flrig:
            logger.error('Flrig is not connected')
            return

        if freq is not None:
            if self.last_freq != freq:
                self.flrig.rig.set_frequency(float(freq))
                self.last_freq = freq

        native_mode = self.CORE_TO_NATIVE_MODES.get(mode, mode) if mode else None
        if not native_mode:
            return
        if not native_mode in self.NATIVE_TO_CORE_MODES.keys():
            logger.warning(f'Unmapped Core Mode: {native_mode}')
            return None
        if self.last_mode != mode:
            self.flrig.rig.set_mode(native_mode)
            self.last_mode = mode

    def get_new_freq(self) -> int | None:
        if not self.flrig:
            logger.error('Flrig is not connected')
            return None
        raw = self.flrig.rig.get_vfo()
        if raw is None:
            logger.error('Failed to get frequency from Flrig')
            return None
        freq = _int_from_xmlrpc(raw)
        if freq != self.last_freq:
            self.last_freq = freq
            return freq
        return None

    def get_new_mode(self) -> str | None:
        if not self.flrig:
            logger.error('Flrig is not connected')
            return None
        raw = self.flrig.rig.get_mode()
        if raw is None:
            logger.error('Failed to get mode from Flrig')
            return None
        native_mode = str(raw)
        mode = self.NATIVE_TO_CORE_MODES.get(native_mode)
        if not mode:
            logger.warning(f'Unmapped Native Mode: {native_mode}')
            return None
        if mode != self.last_mode:
            self.last_mode = mode
            return mode
        return None
