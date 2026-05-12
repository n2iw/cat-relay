from dataclasses import dataclass

from clients.base_client import BaseClient
from config import SDR_CONNECT, SDR_PP, N1MM, DXLAB, RUMLOG, FLRIG, QLOG
from clients.dxlab import CommanderClient
from clients.flrig import FlrigClient
from clients.n1mm import N1MMClient
from clients.sdr_connect import SdrConnectClient
from clients.hamlib import HamlibClient

NAME = 'name'
DEFAULT_PORT = 'default_port'
CLIENT_CLASS = 'client_class'
FIXED_PORT = 'fixed_port'

@dataclass
class Registry:
    name: str
    default_port: int
    fixed_port: bool
    client_class: type[BaseClient]
    def create_client(self, ip: str, port: int) -> BaseClient:
        return self.client_class(ip, port, self.name)

client_registry: dict[str, Registry] = {
    SDR_CONNECT: Registry(SDR_CONNECT, 5454, True, SdrConnectClient),
    SDR_PP: Registry(SDR_PP, 4532, False, HamlibClient),
    DXLAB: Registry(DXLAB, 52002, False, CommanderClient),
    RUMLOG: Registry(RUMLOG, 5555, False, CommanderClient),
    N1MM: Registry(N1MM, 12060, False, N1MMClient),
    FLRIG: Registry(FLRIG, 12345, False, FlrigClient),
    QLOG: Registry(QLOG, 4532, False, HamlibClient)
}