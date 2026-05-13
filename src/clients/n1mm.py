import logging
import socket
import asyncio

from clients.utils.n1mm_radio_info import get_radio_info, set_frequency_message
from clients.base_client import CoreMode, DataNotAvailableException, BaseClient
from clients.utils.mode_mapper import ModeMapper

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
    N1MM_RECEIVE_PORT = 13064
    N1MM_TIMEOUT = 30

    def __init__(self):
        super().__init__()
        self.transport: asyncio.DatagramTransport | None = None
        self._last_mode = ''
        self._last_freq = 0
        self._received_data = True
        self._timed_out = False
        asyncio.create_task(self.detect_disconnection())

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        if not data:
            logger.error('No data received')
        freq, mode = parse_frequency_mode(data.decode('utf-8'))
        if freq:
            self._received_data = True
            self._last_freq = freq
        if mode:
            self._received_data = True
            self._last_mode = mode

    async def detect_disconnection(self):
        while True:
            self._received_data = False
            await asyncio.sleep(self.N1MM_TIMEOUT)
            if not self._received_data:
                self._timed_out = True

    def get_freq(self) -> int:
        if self._timed_out:
            raise Exception('N1MM+ timed out!')
        return self._last_freq

    def get_mode(self) -> str:
        if self._timed_out:
            raise Exception('N1MM+ timed out!')
        return self._last_mode

class N1MMClient(BaseClient):
    def __init__(self, ip: str, port: int, name: str = 'N1MM+') -> None:
        self._ip = ip
        self.listen_port = port
        self.name = name
        self._send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.terminated = False # flag to terminate the thread
        self.thread = None
        self._mapper = ModeMapper({}, {})
        self.n1mm: N1MMProtocol | None = None
        self._listen_transport: asyncio.DatagramTransport | None = None

    async def __aenter__(self) -> 'N1MMClient':
        if self.n1mm is None:
            loop = asyncio.get_running_loop()
            self._listen_transport, self.n1mm = await loop.create_datagram_endpoint(
                lambda: N1MMProtocol(),
                local_addr=('0.0.0.0', self.listen_port)
            )
            if not self._listen_transport or not self.n1mm:
                raise Exception(f'Fail to create {self.name} radio info endpoint')
        return self

    async def send(self, message):
        if isinstance(message, str):
            b_msg = bytes(message, 'utf-8')
        else:
            b_msg = message
        if not self._send_sock:
            logger.error(f'{self.name} send socket not created')
            return
        await asyncio.to_thread(self._send_sock.sendto, b_msg, (self._ip, N1MMProtocol.N1MM_RECEIVE_PORT))

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._send_sock:
            self._send_sock.close()
        if self._listen_transport:
            self._listen_transport.close()
        if self.n1mm:
            self.n1mm = None

    async def get_freq(self) -> int:
        if not self.n1mm:
            raise Exception(f'{self.name} not connected')
        freq = self.n1mm.get_freq()
        if not freq:
            raise DataNotAvailableException(f'{self.name} Frequency not available')
        return self.n1mm.get_freq()

    async def get_mode(self) -> CoreMode:
        if self.n1mm is None:
            raise Exception(f'{self.name} not connected')

        mode = self.n1mm.get_mode()
        if not mode:
            raise DataNotAvailableException(f'{self.name} Mode not available')
        return self._mapper.get_core_mode(mode)

    # Only set frequency, setting mode is not supported in N1MM
    async def set_freq_mode(self, freq: int, mode: CoreMode) -> None:
        cmd = set_frequency_message(freq)
        if cmd:
            await self.send(cmd)