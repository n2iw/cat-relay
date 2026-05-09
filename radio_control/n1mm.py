import logging
import socket
import asyncio

from radio_control.utils.radio_info import get_radio_info, set_frequency_message
from utils.client import CoreMode, Client
from utils.mode_mapper import ModeMapper

logger = logging.getLogger(__name__)


def parse_frequency_mode(data: str) -> tuple[int | None, str | None]:
    info = get_radio_info(data)
    if info:
        freq = info.get_frequency()
        mode = map_mode(info.get_mode(), freq)
        return freq, mode
    else:
        return None, None


# Map 'SSB' to 'USB' or 'LSB' base on frequency
# 'RTTY' to 'USB'
def map_mode(mode, freq):
    if mode == 'SSB':
        return 'USB' if freq > 10_000_000 else 'LSB'
    elif mode == 'RTTY':
        return 'USB'
    return mode

class N1MMProtocol(asyncio.DatagramProtocol):
    def __init__(self):
        super().__init__()
        self.transport: asyncio.DatagramTransport | None = None
        self._last_mode = ''
        self._last_freq = 0

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        if not data:
            logger.error('No data received')
        freq, mode = parse_frequency_mode(data.decode('utf-8'))
        if freq:
            self._last_freq = freq
            self._last_mode = mode

    def get_freq(self) -> int:
        return self._last_freq

    def get_mode(self) -> str:
        return self._last_mode

class N1MMClient(Client):
    def __init__(self, listen_port, send_ip, send_port):
        self.listen_port = listen_port
        self.send_ip = send_ip
        self.send_port = send_port
        self._send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.terminated = False # flag to terminate the thread
        self.thread = None
        self._mapper = ModeMapper({}, {})
        self.n1mm: N1MMProtocol | None = None
        self._listen_transport: asyncio.DatagramTransport = None

    async def __aenter__(self) -> 'N1MMClient':
        if self.n1mm is None:
            loop = asyncio.get_running_loop()
            self._listen_transport, self.n1mm = await loop.create_datagram_endpoint(
                lambda: N1MMProtocol(),
                local_addr=('0.0.0.0', self.listen_port)
            )
            if not self._listen_transport or not self.n1mm:
                raise Exception('Fail to create N1MM radio info endpoint')
        return self

    async def send(self, message):
        if isinstance(message, str):
            b_msg = bytes(message, 'utf-8')
        else:
            b_msg = message
        if not self._send_sock:
            logger.error('Send socket not created')
            return
        await asyncio.to_thread(self._send_sock.sendto, b_msg, (self.send_ip, self.send_port))

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._send_sock:
            self._send_sock.close()
        if self._listen_transport:
            self._listen_transport.close()
        if self.n1mm:
            self.n1mm = None

    async def get_freq(self) -> int:
        if not self.n1mm:
            raise Exception('N1MM not connected')
        freq = self.n1mm.get_freq()
        if not freq:
            raise Exception('N1MM Frequency not available')
        return self.n1mm.get_freq()

    async def get_mode(self) -> CoreMode:
        if self.n1mm is None:
            raise Exception('N1MM not connected')

        mode = self.n1mm.get_mode()
        if not mode:
            raise Exception('N1MM Mode not available')
        return self._mapper.get_core_mode(mode)

    # Only set frequency, setting mode is not supported in N1MM
    async def set_freq_mode(self, freq: int, mode: CoreMode) -> None:
        cmd = set_frequency_message(freq)
        if cmd:
            await self.send(cmd)