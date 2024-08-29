import os
import yaml

SDR_IP = 'SDR_IP'
SDR_PORT = 'SDR_PORT'

CAT_IP = 'CAT_IP'
CAT_PORT = 'CAT_PORT'

RADIO_INFO_PORT = 'RADIO_INFO_PORT'

RECONNECT_TIME = 'RECONNECT_TIME'  # seconds
SYNC_INTERVAL = 'SYNC_TIME'  # seconds

CAT_SOFTWARE = 'CAT_Software'
PLACEHOLDER_SOFTWARE = '--select your software--'
DXLAB = 'DXLab'
RUMLOG = 'RUMLogNG'
N1MM = 'N1MM'
FLRIG = 'FLRIG'
VALID_CAT_SOFTWARES = [DXLAB, RUMLOG, N1MM, FLRIG]

CONFIG_FILE = 'cat-relay.yml'

class Parameters:
    def __init__(self,
                sdr_ip='127.0.0.1',
                sdr_port=4532,
                cat_software=RUMLOG,
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

    def set_sdr_ip(self, ip):
        self.sdr_ip = ip

    def set_sdr_port(self, port):
        self.sdr_port = port

    def set_cat_software(self, software):
        print(f"setting cat software to {software}")
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
        self.config_file_full_path = None
        self.default_config_file_full_path = os.path.join(home_dir, CONFIG_FILE)
        for location in config_file_locations:
            config_file_full_path = os.path.join(location, CONFIG_FILE)
            if os.path.isfile(config_file_full_path):
                try:
                    print(f'Config file {config_file_full_path} found, reading configuration...')
                    with open(config_file_full_path) as c_file:
                        file_config = yaml.safe_load(c_file)
                        self.update_params_from(file_config)
                        self.config_file_full_path = config_file_full_path
                        break
                except Exception as e:
                    print(e)

    def update_params_from(self, params_dict):
        self.params.sdr_ip = params_dict.get(SDR_IP, self.params.sdr_ip)
        self.params.sdr_port = params_dict.get(SDR_PORT, self.params.sdr_port)
        self.params.cat_software = params_dict.get(CAT_SOFTWARE, self.params.cat_software)
        self.params.cat_ip = params_dict.get(CAT_IP, self.params.cat_ip)
        self.params.cat_port = params_dict.get(CAT_PORT, self.params.cat_port)
        self.params.radio_info_port = params_dict.get(RADIO_INFO_PORT, self.params.radio_info_port)
        self.params.reconnect_time = params_dict.get(RECONNECT_TIME, self.params.reconnect_time)
        self.params.sync_interval = params_dict.get(SYNC_INTERVAL, self.params.sync_interval)

    def get_data(self):
        return {
            SDR_IP: self.params.sdr_ip,
            SDR_PORT: self.params.sdr_port,
            CAT_SOFTWARE: self.params.cat_software,
            CAT_IP: self.params.cat_ip,
            CAT_PORT: self.params.cat_port,
            RADIO_INFO_PORT: self.params.radio_info_port,
            RECONNECT_TIME: self.params.reconnect_time,
            SYNC_INTERVAL: self.params.sync_interval
        }

    def save_to_file(self):
        config_file_path = None
        # Updating existing config file
        if self.config_file_full_path and os.path.isfile(self.config_file_full_path):
            config_file_path = self.config_file_full_path
            print(f'Updating config file at {config_file_path}')
        else: # create a new config file in HOME folder
            print(f'Creating new config file at {config_file_path}')
            config_file_path = self.default_config_file_full_path

        print(self.get_data())
        with open(config_file_path, 'w') as c_file:
            yaml_str = yaml.dump(self.get_data())
            print(yaml_str)
            c_file.write(yaml_str)

