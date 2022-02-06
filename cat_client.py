from tcp_client import TCPClient


class CATClient(TCPClient):
    ALTERNATIVE_MODES = {
        'RTTY': 'USB',  # RTTY mode from radio will be mapped to USB mode
        'WFM': 'FM',  # WFM mode from SDR++ will be mapped to FM mode
        'RAW': None,  # RAW mode from SDR++ will be disabled
        'DSB': None  # DSB mode from SDR++ will be disabled
    }

    def map_mode(self, mode):
        valid_mode = mode
        if mode in self.ALTERNATIVE_MODES:
            valid_mode = self.ALTERNATIVE_MODES[mode]

        return valid_mode