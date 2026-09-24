"""Bit fields used by VT HID command reports."""

from busylight_core.word import BitField


class ReportField(BitField):
    """Eight-bit HID report identifier field."""

    def __init__(self) -> None:
        super().__init__(32, 8)


class ActionField(BitField):
    """Eight-bit VT command action field."""

    def __init__(self) -> None:
        super().__init__(24, 8)


class RedField(BitField):
    """Eight-bit red or first command data field."""

    def __init__(self) -> None:
        super().__init__(16, 8)


class GreenField(BitField):
    """Eight-bit green or second command data field."""

    def __init__(self) -> None:
        super().__init__(8, 8)


class BlueField(BitField):
    """Eight-bit blue or third command data field."""

    def __init__(self) -> None:
        super().__init__(0, 8)
