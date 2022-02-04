import xml.etree.ElementTree as ET

FREQUENCY = 'Freq1'


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

    def __init__(self, root):
        if root.tag == self.TAG_NAME:
            self.data = {}
            for element in self.elements:
                value = read_child(root, element)
                if value is not None:
                    self.data[element] = value
        else:
            raise f'Data received is not a RadioInfo data'

