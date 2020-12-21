"""
"""

from bitvector import BitVector


class State(BitVector):
    def __init__(self, value: int, size: int):
        super().__init__(value, size)
        self.default_value = value

    def reset(self):
        self.value = self.default_value

    def __bytes__(self):
        return self.bytes
