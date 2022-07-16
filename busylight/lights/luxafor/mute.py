""" Luxafor Mute Support
"""

from loguru import logger

from .flag import Flag


class Mute(Flag):

    SUPPORTED_DEVICE_IDS = {
        (0x4D8, 0xF372): "Mute",
    }

    @property
    def state(self) -> bool:
        """Returns the current state of the button.

        True is pressed, False is released.
        """

        results = self.read_strategy(8, 200)

        try:
            if results[0] == 66:
                self._button = False

            if results[0] == 131:
                return bool(results[1])

        except IndexError:
            pass
        return False
