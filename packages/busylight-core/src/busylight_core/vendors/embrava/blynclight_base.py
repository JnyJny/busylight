"""Embrava Blynclight family base class."""

from .blynclight_protocol import BlynclightProtocol
from .embrava_base import EmbravaBase


class BlynclightBase(BlynclightProtocol, EmbravaBase):
    """Base class for Embrava Blynclight family devices.

    Combines Embrava vendor identity with the core Blynclight USB
    protocol. Provides color, dim/bright, flash, and device state
    management. Does not include sound capabilities -- see
    BlynclightPlus for the extended feature set.
    """
