import logging

from clients.base_client import CoreMode

logger = logging.getLogger(__name__)

class ModeMapper:
    """
    Maps between core modes and native modes
    """

    default_native_to_core_mapping = {
        'FM': CoreMode.FM,
        'AM': CoreMode.AM,
        'USB': CoreMode.USB,
        'LSB': CoreMode.LSB,
        'CW': CoreMode.CW
    }

    default_core_to_native_mapping = {
        CoreMode.FM: 'FM',
        CoreMode.AM: 'AM',
        CoreMode.USB: 'USB',
        CoreMode.LSB: 'LSB',
        CoreMode.CW: 'CW'
    }

    def __init__(self, core_to_native_mode_mapping: dict[CoreMode, str], native_to_core_mode_mapping: dict[str, CoreMode]):
        self._core_to_native_mode_mapping = self.default_core_to_native_mapping | core_to_native_mode_mapping
        self._native_to_core_mode_mapping = self.default_native_to_core_mapping | native_to_core_mode_mapping

    def get_native_mode(self, core_mode: CoreMode) -> str:
        return self._core_to_native_mode_mapping.get(core_mode, core_mode.value)

    def get_core_mode(self, native_mode: str) -> CoreMode:
        core_mode = self._native_to_core_mode_mapping.get(native_mode)
        if core_mode is None:
            logger.warning(f'Unmapped native mode: {native_mode}')
            return CoreMode.CW
        else:
            return core_mode