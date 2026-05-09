import logging
import socket
import threading

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


class N1MMClient(Client):
    def __init__(self, listen_port, send_ip, send_port):
        self.listen_port = listen_port
        self.send_ip = send_ip
        self.send_port = send_port
        self.listen_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._last_mode = ''
        self._last_freq = 0
        self.terminated = False # flag to terminate the thread
        self.thread = None
        self._mapper = ModeMapper({}, {})

    async def __aenter__(self) -> 'N1MMClient':
        if not self.listen_sock or not self.send_sock:
            logger.error('Listen or send socket not created')
            raise Exception('Listen or send socket not created')
        self.listen_sock.bind(('0.0.0.0', self.listen_port))
        self.thread = threading.Thread(target=self.listen)
        self.thread.start()
        return self

    # This function will be running in a separate thread and updates self.last_mode and self.last_freq
    def listen(self):
        logger.info('listening UDP in a new thread')
        while True:
            if self.terminated:
                logger.info('Terminated flag detected, terminate the thread')
                return
            data = self.receive()
            if not data:
                logger.error('No data received')
                continue
            freq, mode = parse_frequency_mode(data)
            if freq:
                self._last_freq = freq
                self._last_mode = mode

    def send(self, message):
        if isinstance(message, str):
            b_msg = bytes(message, 'utf-8')
        else:
            b_msg = message
        if not self.send_sock:
            logger.error('Send socket not created')
            return
        self.send_sock.sendto(b_msg, (self.send_ip,  self.send_port))

    def receive(self) -> str | None:
        if not self.listen_sock:
            logger.error('Listen socket not created')
            return None
        data, addr = self.listen_sock.recvfrom(1024)  # buffer size is 1024 bytes
        return data.decode('utf-8')

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        self.terminated = True
        if self.thread:
            self.thread.join()
        if self.listen_sock:
            self.listen_sock.close()
            self.listen_sock = None
        if self.send_sock:
            self.send_sock.close()
            self.send_sock = None

    async def get_freq(self) -> int:
        return self._last_freq

    async def get_mode(self) -> CoreMode:
        if not self._last_mode:
            raise Exception('Mode is not set')
        return self._mapper.get_core_mode(self._last_mode)

    # Only set frequency, setting mode is not supported in N1MM
    async def set_freq_mode(self, freq: int, mode: CoreMode) -> None:
        cmd = set_frequency_message(freq)
        if cmd:
            self._last_freq = freq
            self._last_mode = self._mapper.get_native_mode(mode)
            self.send(cmd)