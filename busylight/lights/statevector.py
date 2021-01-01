"""a Compact Device State Representation.
"""


from bitvector import BitVector, BitField, ReadOnlyBitField


class StateField(BitField):
    """A bit field in a state vector."""


class ReadOnlyStateField(ReadOnlyBitField):
    """A read-only bit field in a state vector."""


class StateVector(BitVector):
    """A State Vector composed of bit fields.

    The StateVector class is designed to represent a hardware device's
    current state.
    """

    def __init__(self, value: int, size: int):
        super().__init__(value, size)
        self.default_value = value

    def reset(self):
        """Resets the state vector to the initial value."""
        self.value = self.default_value

    def __bytes__(self):
        """Returns a `bytes` representation of the state vector."""
        return self.bytes
