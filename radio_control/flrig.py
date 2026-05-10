import logging
import asyncio
import xmlrpc.client
from utils.client import CoreMode, Client
from utils.mode_mapper import ModeMapper

from radio_control.utils.transport import RequestsTransport

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
        self._mapper = ModeMapper(self.CORE_TO_NATIVE_MODES, self.NATIVE_TO_CORE_MODES)

    async def __aenter__(self) -> 'FlrigClient':
        self._flrig = await asyncio.to_thread(
            xmlrpc.client.ServerProxy,
            'http://{}:{}/'.format(self._ip, self._port),
            transport=RequestsTransport(use_builtin_types=True),
            allow_none=True)
        if not self._flrig:
            raise Exception('Fail to connect to Flrig')
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._flrig:
            await asyncio.to_thread(self._flrig("close"))
            self._flrig = None

    async def set_freq_mode(self, freq: int, mode: CoreMode) -> None:
        if not self._flrig:
            logger.error('Flrig is not connected')
            return

        if await self.get_freq() != freq:
            await asyncio.to_thread(self._flrig.rig.set_frequency, float(freq))

        native_mode = self._mapper.get_native_mode(mode)
        if native_mode not in self.NATIVE_TO_CORE_MODES.keys():
            logger.warning(f'Unmapped Core Mode: {mode}')
            return
        if await self.get_mode() != mode:
            self._flrig.rig.set_mode(native_mode)

    async def get_freq(self) -> int:
        if not self._flrig:
            raise Exception('Flrig is not connected')
        raw = await asyncio.to_thread(self._flrig.rig.get_vfo)
        if raw is None:
            raise Exception('Failed to get frequency from Flrig')
        freq = _int_from_xmlrpc(raw)
        return freq

    async def get_mode(self) -> CoreMode:
        if not self._flrig:
            raise Exception('Flrig is not connected')
        raw = await asyncio.to_thread(self._flrig.rig.get_mode)
        if raw is None:
            raise Exception('Failed to get mode from Flrig')
        native_mode = str(raw)
        return self._mapper.get_core_mode(native_mode)