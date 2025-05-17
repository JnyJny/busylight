""" Luxafor Mute
"""

from typing import Dict, Tuple

from loguru import logger

from .flag import Flag


class Mute(Flag):
    @staticmethod
    def supported_device_ids() -> Dict[Tuple[int, int], str]:
        return {
            (0x4D8, 0xF372): "Mute",
        }

    @property
    def is_button(self) -> bool:
        return True

    @property
    def button_on(self) -> bool:

        results = self.read_strategy(8, 200)

        try:
            if results[0] == 66:
                self._button = False  # ???

            if results[0] == 131:
                return bool(results[1])
        except IndexError:
            pass

        return False
