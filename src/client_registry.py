from config import SDR_CONNECT, SDR_PP, N1MM, DXLAB, RUMLOG, FLRIG, HAMLIB
from clients.dxlab import Commander
from clients.flrig import FlrigClient
from clients.n1mm import N1MMClient
from clients.sdr_connect import SdrConnectClient
from clients.sdr_pp import SdrPPClient

DEFAULT_PORT = 'default_port'
CLIENT_CLASS = 'client_class'
FIXED_PORT = 'fixed_port'

client_registry = {
    SDR_CONNECT: {
        DEFAULT_PORT: '5454',
        FIXED_PORT: True,
        CLIENT_CLASS: SdrConnectClient
    },
    SDR_PP: {
        DEFAULT_PORT: '4532',
        CLIENT_CLASS: SdrPPClient
    },
    DXLAB: {
        DEFAULT_PORT: '52002',
        CLIENT_CLASS: Commander
    },
    RUMLOG: {
        DEFAULT_PORT: '5555',
        CLIENT_CLASS: Commander
    },
    N1MM: {
        DEFAULT_PORT: '12060',
        CLIENT_CLASS: N1MMClient
    },
    FLRIG: {
        DEFAULT_PORT: '12345',
        CLIENT_CLASS: FlrigClient
    },
    HAMLIB: {
        DEFAULT_PORT: '4532',
        CLIENT_CLASS: SdrPPClient
    }
}