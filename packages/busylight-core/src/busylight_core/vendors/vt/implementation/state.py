"""VT DND device state management.

This module defines the State class that builds the 5-byte HID
command reports sent to VT DND devices.
"""

from busylight_core.word import Word

from .enums import Action, Brightness, FlashMode, Report
from .fields import ActionField, DataField, ReportField


class State(Word):
    """Command report for VT DND devices.

    Each report holds a single command: a report number, an action,
    and three argument bytes whose meaning depends on the action.
    """

    def __init__(self) -> None:
        super().__init__(0, 40)

    report = ReportField(32, 8)
    action = ActionField(24, 8)

    data0 = DataField(16, 8)
    data1 = DataField(8, 8)
    data2 = DataField(0, 8)

    @property
    def data(self) -> tuple[int, int, int]:
        """Get the command argument bytes as a tuple."""
        return (self.data0, self.data1, self.data2)

    @data.setter
    def data(self, values: tuple[int, int, int]) -> None:
        """Set the command argument bytes from a tuple."""
        self.data0, self.data1, self.data2 = values

    def command(self, action: Action, data: tuple[int, int, int] = (0, 0, 0)) -> None:
        """Replace the current report with a new command.

        :param action: Command to execute
        :param data: Command argument bytes
        """
        self.clear()
        self.report = Report.ONE
        self.action = action
        self.data = data

    def set_color(self, color: tuple[int, int, int]) -> None:
        """Configure a command to display a steady RGB color.

        :param color: RGB values from 0-255
        """
        self.command(Action.SetColor, color)

    def set_brightness(self, level: Brightness) -> None:
        """Configure a command to change the brightness level.

        :param level: Brightness level to apply
        """
        self.command(Action.SetBrightness, (level, 0, 0))

    def flash(self, mode: FlashMode) -> None:
        """Configure a command to start a predefined flash pattern.

        :param mode: Firmware flash pattern to run
        """
        self.command(Action.Flash, (mode, 0, 0))

    def off(self) -> None:
        """Configure a command to turn the light off."""
        self.command(Action.Off)
