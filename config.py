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

class Parameters:
    def __init__(self,
                sdr_ip='127.0.0.1',
                sdr_port=4532,
                cat_software=DXLAB,
                cat_ip='127.0.0.1',
                cat_port=5555,
                radio_info_port=13063,
                reconnect_time=10,
                sync_interval=0.05
    ):
        self.sdr_ip = sdr_ip
        self.sdr_port = sdr_port
        self.cat_software = cat_software
        self.cat_ip = cat_ip
        self.cat_port = cat_port
        self.radio_info_port = radio_info_port
        self.reconnect_time = reconnect_time
        self.sync_interval = sync_interval

    def update_from(self, params_dict):
        self.sdr_ip = params_dict.get(SDR_IP, self.sdr_ip)
        self.sdr_port = params_dict.get(SDR_PORT, self.sdr_port)
        self.cat_software = params_dict.get(CAT_SOFTWARE, self.cat_software).lower()
        self.cat_ip = params_dict.get(CAT_IP, self.cat_ip)
        self.cat_port = params_dict.get(CAT_PORT, self.cat_port)
        self.radio_info_port = params_dict.get(RADIO_INFO_PORT, self.radio_info_port)
        self.reconnect_time = params_dict.get(RECONNECT_TIME, self.reconnect_time)
        self.sync_interval = params_dict.get(SYNC_INTERVAL, self.sync_interval)

    def set_sdr_ip(self, ip):
        self.sdr_ip = ip

    def set_sdr_port(self, port):
        self.sdr_port = port

    def set_cat_software(self, software):
        self.cat_software = software

    def set_cat_ip(self, ip):
        self.cat_ip = ip

    def set_cat_port(self, port):
        self.cat_port = port

    def set_radio_info_port(self, port):
        self.radio_info_port = port

    def set_reconnect_time(self, seconds):
        self.reconnect_time = seconds

    def set_sync_interval(self, seconds):
        self.sync_interval = seconds

class Config:
    def __init__(self):
        self.params = Parameters()

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
                        self.params.update_from(file_config)
                        break
                except Exception as e:
                    print(e)
        pprint.pp(self.params, indent=4)