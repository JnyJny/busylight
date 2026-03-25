"""Base BlinkStick Implementation"""

from .agile_innovative_base import AgileInnovativeBase
from .implementation import State


class BlinkStickBase(AgileInnovativeBase):
    """Base BlinkStick Implementation

    Subclasses should provide a claims classmethod and a state
    instance property that provides a properly initialized State
    instance for the specific BlinkStick variant.
    """

    @staticmethod
    def get_version(serial_number: str) -> tuple[int, int]:
        """Extract the major and minor version from the hardware serial number.

        Raises:
        - ValueError: If the serial number does not contain a valid version.

        """
        if not serial_number or not serial_number.startswith("BS"):
            msg = "Invalid BlinkStick serial number"
            raise ValueError(msg)

        try:
            return map(int, serial_number[-3:].split("."))
        except (IndexError, TypeError, ValueError):
            raise ValueError from None

    @staticmethod
    def vendor() -> str:
        """Return the vendor name for this device."""
        return "Agile Innovative"

    @property
    def state(self) -> State:
        """BlinkStick in-memory state."""
        raise NotImplementedError

    @property
    def nleds(self) -> int:
        """The number of individually addressable LEDs."""
        return self.state.nleds

    def __bytes__(self) -> bytes:
        """Return the byte representation of the BlinkStick state."""
        return bytes(self.state)

    def _on(self, color: tuple[int, int, int], led: int = 0) -> None:
        """Activate the light with the given red, green, blue color tuple.

        :param color: RGB color tuple (red, green, blue) with values 0-255
        :param led: LED index (0 for main LED, 1+ for additional LEDs)
        """
        with self.batch_update():
            if led == 0:
                self.color = color
            else:
                self.state.set_led(led - 1, color)

    @property
    def color(self) -> tuple[int, int, int]:
        """Tuple of RGB color values."""
        return self.state.color

    @color.setter
    def color(self, value: tuple[int, int, int]) -> None:
        self.state.color = value
