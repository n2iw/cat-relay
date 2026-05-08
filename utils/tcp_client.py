import asyncio
import re
import logging

BUFFER_SIZE = 1024
SOCKET_TIMEOUT = 1

logger = logging.getLogger(__name__)

class TCPClient:
    def __init__(self, ip: str, port: int):
        self._ip = ip
        self._port = port
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None

    async def open(self):
        self._reader, self._writer = await asyncio.open_connection(self._ip, self._port, timeout=SOCKET_TIMEOUT)
        return self

    async def send(self, message: str) -> None:
        if not self._writer:
            logger.error('Socket not connected')
            return
        self._writer.write(bytes(message, 'utf-8'))
        await self._writer.drain()

    async def receive(self) -> str | None:
        if not self._reader:
            logger.error('Socket not connected')
            return None
        msg = await self._reader.read(BUFFER_SIZE)
        result = re.match(r"b\'(.+)\'", str(msg))
        if result:
            return result.group(1)
        return None

    async def close(self) -> None:
        if self._writer:
            self._writer.close()
            await self._writer.wait_closed()
            self._writer = None

        if self._reader:
            self._reader.feed_eof()
            self._reader = None
