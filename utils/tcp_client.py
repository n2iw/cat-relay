import re
import socket
import logging
from abc import abstractmethod, ABC

BUFFER_SIZE = 1024
SOCKET_TIMEOUT = 1

logger = logging.getLogger(__name__)

class TCPClient(ABC):
    @abstractmethod
    def _enter(self) -> None:
        ...

    def __init__(self, ip: str, port: int):
        self._ip = ip
        self._port = port
        self._sock: socket.socket | None = None

    def __enter__(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(SOCKET_TIMEOUT)
        self._sock.connect((self._ip, self._port))
        self._enter()
        return self

    def send(self, message: str) -> None:
        if not self._sock:
            logger.error('Socket not connected')
            return
        self._sock.send(bytes(message, 'utf-8'))

    def receive(self) -> str | None:
        if not self._sock:
            logger.error('Socket not connected')
            return None
        msg = str(self._sock.recv(BUFFER_SIZE))
        result = re.match(r"b\'(.+)\'", str(msg))
        if result:
            return result.group(1)

    def close(self) -> None:
        if self._sock:
            self._sock.close()
            self._sock = None

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
