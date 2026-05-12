from config import SDR_CONNECT, SDR_PP, N1MM, DXLAB, RUMLOG, FLRIG

DEFAULT_PORT = 'default_port'
DEFAULT_RADIO_INFO_PORT = 'default_radio_info_port'

client_registry = {
    SDR_CONNECT: {
        DEFAULT_PORT: '5454'
    },
    SDR_PP: {
        DEFAULT_PORT: '4532'
    },
    DXLAB: {
        DEFAULT_PORT: '52002'
    },
    RUMLOG: {
        DEFAULT_PORT: '5555'
    },
    N1MM: {
        DEFAULT_RADIO_INFO_PORT: '12060'
    },
    FLRIG: {
        DEFAULT_PORT: '12345'
    }
}