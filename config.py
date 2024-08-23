import os
import yaml

SDR_IP = 'SDR_IP'
SDR_PORT = 'SDR_PORT'

RADIO_CONTROL_IP = 'Radio_Control_IP'
RADIO_CONTROL_PORT = 'Radio_Control_PORT'

RADIO_INFO_PORT = 'RADIO_INFO_PORT'

RETRY_TIME = 'Reconnect_time'  # seconds
SYNC_INTERVAL = 'Sync_time'  # seconds

RADIO_CONTROL_SOFTWARE = 'Radio_Control_Software'
DXLAB = 'dxlab'
N1MM = 'n1mm'
FLRIG = 'flrig'

CONFIG_FILE = 'config.yml'

class Parameters:
    def __init__(self):
        self.config = {
            SDR_IP: '127.0.0.1',
            SDR_PORT:  4532,

            RADIO_CONTROL_IP: '127.0.0.1',
            RADIO_CONTROL_PORT: 5555,

            RADIO_INFO_PORT: 13063,

            RETRY_TIME: 10,  # seconds
            SYNC_INTERVAL: 0.05,  # seconds

            RADIO_CONTROL_SOFTWARE: DXLAB
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
                        self.config[RADIO_CONTROL_SOFTWARE] = self.config[RADIO_CONTROL_SOFTWARE].lower()
                        break
                except Exception as e:
                    print(e)
        print(self.config)

    def get_logger_mode(self):
        return self.config[RADIO_CONTROL_SOFTWARE]

    def get_logger_ip(self):
        return self.config[RADIO_CONTROL_IP]

    def get_logger_port(self):
        return self.config[RADIO_CONTROL_PORT]

    def get_radio_info_port(self):
        return self.config[RADIO_INFO_PORT]

    def get_sdr_ip(self):
        return self.config[SDR_IP]

    def get_sdr_port(self):
        return self.config[SDR_PORT]

    def get_sync_interval(self):
        return self.config[SYNC_INTERVAL]

    def get_retry_time(self):
        return self.config[RETRY_TIME]
