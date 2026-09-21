"""VT HID report state."""

from busylight_core.word import Word

from .fields import (
    ActionField,
    BlueField,
    GreenField,
    RedField,
    ReportField,
)


class State(Word):
    """Track VT report fields and the current brightness level."""

    def __init__(self) -> None:
        self._brightness = 2
        super().__init__(0, 40)

    report = ReportField()
    action = ActionField()
    red = RedField()
    green = GreenField()
    blue = BlueField()

    @property
    def brightness(self) -> int:
        """Return the currently tracked brightness level."""
        return self._brightness

    @brightness.setter
    def brightness(self, value: int) -> None:
        """Track a brightness level between one and three."""
        if not 1 <= value <= 3:
            message = "brightness must be between 1 and 3"
            raise ValueError(message)
        self._brightness = value

    @property
    def color(self) -> tuple[int, int, int]:
        """Get the current RGB color as a tuple."""
        return (self.red, self.green, self.blue)

    @color.setter
    def color(self, values: tuple[int, int, int]) -> None:
        """Set the RGB color from a tuple."""
        self.red, self.green, self.blue = values
