"""Luxafor Mute"""

from typing import ClassVar

from .flag import Flag


class Mute(Flag):
    """Luxafor Mute status light controller.

    A mute button device with status light functionality, combining
    the Luxafor Flag features with button input capabilities.
    """

    supported_device_ids: ClassVar[dict[tuple[int, int], str]] = {
        (0x4D8, 0xF372): "Mute",
    }

    @property
    def is_button(self) -> bool:
        """Return True if this device has button functionality."""
        return True

    @property
    def button_on(self) -> bool:
        """Return True if the mute button is currently pressed."""
        # EJO The Mute device returns:
        #     - [131, 0, 0, 0, 0, 0, 0, 0] on push
        #     - [131, 1, 0, 0, 0, 0, 0, 0] on release
        #
        #     this device needs an async coroutine to update the
        #     button state [pushed/released] since it's unlikely that
        #     this property will be polled at the right time to catch
        #     the button state change.
        #
        #     Sometimes there is a [66, 0, 0, 0, 0, 0, 0, 0] but I'll
        #     have to refer to the documentation to figure out what
        #     that signifies.
        #
        #     Until these issues are resolved, this method is busted.

        results = self.read_strategy(8, 200)

        try:
            if results[0] == 131:
                return bool(results[1])
        except IndexError:
            pass

        return False
