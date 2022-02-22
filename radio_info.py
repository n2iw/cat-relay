import xml.etree.ElementTree as ET

FREQUENCY = 'Freq1'

APP_NAME = 'Cat-Relay'


def read_child(data, name):
    result = None
    child = data.find(name)
    if child is not None:
        result = child.text

    return result


def get_radio_info(xml_data):
    root = ET.fromstring(xml_data)
    if root.tag == RadioInfo.TAG_NAME:
        return RadioInfo(root)
    else:
        print(f'"{root.tag}" tag received, but not supported!')

    return None


def set_frequency_message(freq):
    cmd = ET.Element('radio_setfrequency')
    app = ET.SubElement(cmd, 'app')
    app.text = APP_NAME
    radio_nr = ET.SubElement(cmd, 'radionr')
    radio_nr.text = '1'
    frequency = ET.SubElement(cmd, 'frequency')
    frequency.text = f'{freq/1000:.3f}'
    message = ET.tostring(cmd, xml_declaration=True)
    return message


class RadioInfo:
    TAG_NAME = 'RadioInfo'
    elements = [
        'StationName',
        'RadioNr',
        'Freq',
        'TXFreq',
        'Mode',
        'FocusRadioNr'
    ]

    def get_frequency(self):
        '''
        :return: frequency in Hz
        '''
        if self.data and 'Freq' in self.data:
            return int(self.data['Freq']) * 10

    def get_mode(self):
        '''
        :return: mode
        '''
        if self.data and 'Mode' in self.data:
            return self.data['Mode']

    def __init__(self, root):
        if root.tag == self.TAG_NAME:
            self.data = {}
            for element in self.elements:
                value = read_child(root, element)
                if value is not None:
                    self.data[element] = value
        else:
            raise f'Data received is not a RadioInfo data'

