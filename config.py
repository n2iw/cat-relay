import os
import yaml
import pprint

SDR_IP = 'SDR_IP'
SDR_PORT = 'SDR_PORT'

CAT_IP = 'CAT_IP'
CAT_PORT = 'CAT_PORT'

RADIO_INFO_PORT = 'RADIO_INFO_PORT'

RECONNECT_TIME = 'RECONNECT_TIME'  # seconds
SYNC_INTERVAL = 'SYNC_TIME'  # seconds

CAT_SOFTWARE = 'CAT_Software'
DXLAB = 'dxlab'
N1MM = 'n1mm'
FLRIG = 'flrig'

CONFIG_FILE = 'config.yml'

class Config:
    def __init__(self):
        self.config = {
            SDR_IP: '127.0.0.1',
            SDR_PORT:  4532,

            CAT_SOFTWARE: DXLAB,

            CAT_IP: '127.0.0.1',
            CAT_PORT: 5555,

            RADIO_INFO_PORT: 13063,

            RECONNECT_TIME: 10,  # seconds
            SYNC_INTERVAL: 0.05  # seconds
        }

        script_dir = os.path.dirname(os.path.realpath(__file__))
        work_dir = os.getcwd()
        home_dir = os.environ["HOME"]
        config_file_locations = [work_dir, home_dir, script_dir]
        for location in config_file_locations:
            config_file_full_path = os.path.join(location, CONFIG_FILE)
            if os.path.isfile(config_file_full_path):
                try:
                    print(f'Config file {config_file_full_path} found, reading configuration...')
                    with open(config_file_full_path) as c_file:
                        file_config = yaml.safe_load(c_file)
                        self.config.update(file_config)
                        self.config[CAT_SOFTWARE] = self.config[CAT_SOFTWARE].lower()
                        break
                except Exception as e:
                    print(e)
        pprint.pp(self.config, indent=4)

    def set_cat_software(self, software):
        # print(f'Change Cat Software to "{software}"')
        if software:
            self.config[CAT_SOFTWARE] = software.lower()

    def get_cat_software(self):
        return self.config[CAT_SOFTWARE]

    def set_cat_ip(self, ip):
        # print(f'Change CAT IP to {ip}')
        if ip:
            self.config[CAT_IP] = ip

    def get_cat_ip(self):
        return self.config[CAT_IP]

    def set_cat_port(self, port):
        # print(f'Change CAT PORT to {port}')
        if port:
            self.config[CAT_PORT] = port

    def get_cat_port(self):
        return self.config[CAT_PORT]

    def set_radio_info_port(self, port):
        # print(f'Change Radio Info PORT to {port}')
        if port:
            self.config[RADIO_INFO_PORT] = port

    def get_radio_info_port(self):
        return self.config[RADIO_INFO_PORT]

    def set_sdr_ip(self, ip):
        # print(f'Change SDR IP to {ip}')
        if ip:
            self.config[SDR_IP] = ip

    def get_sdr_ip(self):
        return self.config[SDR_IP]

    def set_sdr_port(self, port):
        # print(f'Change SDR PORT to {port}')
        if port:
            self.config[SDR_PORT] = port

    def get_sdr_port(self):
        return self.config[SDR_PORT]

    def set_sync_interval(self, seconds):
        # print(f'Change Sync time to {seconds}')
        if seconds:
            self.config[SYNC_INTERVAL] = seconds

    def get_sync_interval(self):
        return self.config[SYNC_INTERVAL]

    def set_reconnect_time(self, seconds):
        # print(f'Change reconnect time to {seconds}')
        if seconds:
            self.config[RECONNECT_TIME] = seconds

    def get_reconnect_time(self):
        return self.config[RECONNECT_TIME]
