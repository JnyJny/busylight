"""
"""

from ..statevector import StateField, StateVector


class BusyLightState(StateVector):
    def __init__(self):
        super().__init__(0, 0)
