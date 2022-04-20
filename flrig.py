import xmlrpc.client
from transport import RequestsTransport
from requests.exceptions import ConnectionError

## The following are the valid modes that can be used on my Icom IC-7100. They may require changing for
## your radio. Note that we use two dictionaries here: RADIO_TO_SDR converts the string we get from the
## transceiver to the mode that the SDR can understand. SDR_TO_RADIO converts the SDR string to what the
## radio wants.

## Note that if you want to focus on voice modes, you should probably translate "USB" to "USB"
## instead of "USB" to "USB-D" because USB-D is meant for digital decoding and may mute the rig microphone,
## depending on how you have your USB connection set on the radio. The same is true for "LSB" and "AM" modes.

RADIO_TO_SDR = {
 'LSB':'LSB',
 'USB':'USB',
 'AM':'AM',
 'CW':'CW',
 'RTTY':'USB',
 'FM':'NFM',
 'WFM':'WFM',
 'CW-R':'CW',
 'RTTY-R':'USB',
 'DV':'NFM',
 'LSB-D':'LSB',
 'USB-D':'USB',
 'AM-D':'AM',
 'FM-D':'NFM'
}

SDR_TO_RADIO = {
 'LSB':'LSB-D',
 'USB':'USB-D',
 'AM':'AM-D',
 'DSB':'AM',
 'NFM':'FM',
 'WFM':'WFM',
 'CW':'CW',
 'RAW':'USB'
}

    
class FlrigClient():

    def __init__(self, ip, port):
        self.last_mode = None
        self.last_freq = None
        self._ip = ip
        self._port = port
        self._sock = None

    def __enter__(self):
#        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#        self._sock.connect((self._ip, self._port))
#        self._enter()
#        print(f'Attempting to connect to connect to Flrig at IP address={self._ip}, port={self._port}, via XMP-RPC')
        try:
            self.flrig = xmlrpc.client.ServerProxy('http://{}:{}/'.format(self._ip, self._port), transport=RequestsTransport(use_builtin_types=True), allow_none=True)
        except ConnectionError as e:
            print(e)
            print("Are you sure flrig is running?")
            sys.exit()
        return self

    def __exit__(self, a, b, c):
        return

    def set_freq_mode(self, raw_freq, mode):
        freq = float(raw_freq)
        if freq and self.last_freq != freq:
            self.flrig.rig.set_frequency(freq)
            self.last_freq = freq

        if mode and self.last_mode != mode:
            radiomode = SDR_TO_RADIO[mode]
            self.flrig.rig.set_mode(radiomode)
            self.last_mode = mode

    def get_last_freq(self):
        return int(self.last_freq)

    def get_last_mode(self):
        return self.last_mode

    def get_freq(self):
        self.last_freq = self.flrig.rig.get_vfo()
        return int(self.last_freq)

    def get_mode(self):
        radiomode = self.flrig.rig.get_mode()
        sdrmode = RADIO_TO_SDR[radiomode]
        self.last_mode = sdrmode
        return self.get_last_mode()
