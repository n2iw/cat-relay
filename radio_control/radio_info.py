import logging
import xml.etree.ElementTree as elementTree

FREQUENCY = 'Freq1'

logger = logging.getLogger(__name__)

APP_NAME = 'Cat-Relay'

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

    def get_frequency(self) -> int | None:
        """
        :return: frequency in Hz
        """
        if self.data and 'Freq' in self.data:
            return int(self.data['Freq']) * 10
        return None

    def get_mode(self) -> str | None:
        """
        :return: mode
        """
        if self.data and 'Mode' in self.data:
            return self.data['Mode']
        return None

    def __init__(self, root):
        if root.tag == self.TAG_NAME:
            self.data = {}
            for element in self.elements:
                value = read_child(root, element)
                if value is not None:
                    self.data[element] = value
        else:
            raise Exception(f'Data received is not a RadioInfo data')


def read_child(data, name):
    result = None
    child = data.find(name)
    if child is not None:
        result = child.text

    return result


def get_radio_info(xml_data: str) -> RadioInfo | None:
    root = elementTree.fromstring(xml_data)
    if root.tag == RadioInfo.TAG_NAME:
        return RadioInfo(root)
    else:
        logger.warning('"%s" tag received, but not supported!', root.tag)

    return None


def set_frequency_message(freq):
    cmd = elementTree.Element('radio_setfrequency')
    app = elementTree.SubElement(cmd, 'app')
    app.text = APP_NAME
    radio_nr = elementTree.SubElement(cmd, 'radionr')
    radio_nr.text = '1'
    frequency = elementTree.SubElement(cmd, 'frequency')
    frequency.text = f'{freq/1000:.3f}'
    message = elementTree.tostring(cmd, xml_declaration=True)
    return message

